"""
Recommendation service module
Implements multiple recommendation algorithms:
- Genre-based recommendations
- Popularity-based recommendations (highest ratings)
- Collaborative filtering (similar users)
"""

import logging
from sqlalchemy import func, and_
from app.models import db, Movie, Rating, User, movie_genre, Genre

# Configure logging
logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating movie recommendations"""
    
    @staticmethod
    def get_genre_based_recommendations(user_id, limit=12):
        """
        Get recommendations based on genres the user likes.
        Finds movies in genres that the user has rated highly (4+ stars).
        
        Args:
            user_id: ID of the user
            limit: Maximum number of recommendations to return
        
        Returns:
            List of Movie objects
        """
        # Get user's highly rated movies (4+ stars)
        user_ratings = Rating.query.filter_by(user_id=user_id).filter(Rating.rating >= 4).all()
        
        if not user_ratings:
            return []
        
        # Get genres from highly rated movies
        liked_genres = set()
        for rating in user_ratings:
            for genre in rating.movie.genres:
                liked_genres.add(genre.id)
        
        if not liked_genres:
            return []
        
        # Get movies in the same genres that user hasn't rated
        rated_movie_ids = {r.movie_id for r in Rating.query.filter_by(user_id=user_id).all()}
        
        # Query using the association table
        recommended = Movie.query.filter(
            ~Movie.id.in_(rated_movie_ids) if rated_movie_ids else True
        ).join(movie_genre).filter(
            movie_genre.c.genre_id.in_(liked_genres)
        ).distinct().limit(limit).all()
        
        return recommended
    
    @staticmethod
    def get_popularity_based_recommendations(user_id, limit=12, min_rating=3.5):
        """
        Get recommendations based on movie popularity (highest average ratings).
        Shows highly-rated movies the user hasn't rated yet.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of recommendations
            min_rating: Minimum average rating threshold
        
        Returns:
            List of Movie objects sorted by rating
        """
        try:
            # Get movies user has rated
            rated_movie_ids = db.session.query(Rating.movie_id).filter_by(
                user_id=user_id
            ).all()
            rated_ids = {r[0] for r in rated_movie_ids}
            
            # Subquery to get average ratings
            avg_rating_subquery = db.session.query(
                Rating.movie_id,
                func.avg(Rating.rating).label('avg_rating')
            ).group_by(Rating.movie_id).subquery()
            
            # Get high-rated movies user hasn't seen
            recommendations = db.session.query(Movie, avg_rating_subquery.c.avg_rating).join(
                avg_rating_subquery,
                Movie.id == avg_rating_subquery.c.movie_id
            ).filter(
                ~Movie.id.in_(rated_ids) if rated_ids else True,
                avg_rating_subquery.c.avg_rating >= min_rating
            ).order_by(
                avg_rating_subquery.c.avg_rating.desc()
            ).limit(limit).all()
            
            return [movie for movie, _ in recommendations]
        except Exception as e:
            logger.error(f"Error getting popularity-based recommendations for user {user_id}: {str(e)}")
            return []
    
    @staticmethod
    def get_collaborative_filtering_recommendations(user_id, limit=12, min_similarity=0.3):
        """
        Collaborative filtering recommendations.
        Find users with similar rating patterns and recommend their highly-rated movies.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of recommendations
            min_similarity: Minimum similarity threshold (0-1)
        
        Returns:
            List of Movie objects
        """
        try:
            # Get user's ratings efficiently
            user_ratings = db.session.query(
                Rating.movie_id,
                Rating.rating
            ).filter_by(user_id=user_id).all()
            
            if not user_ratings:
                return []
            
            user_rated_movies = {r[0] for r in user_ratings}
            user_ratings_dict = {r[0]: r[1] for r in user_ratings}
            
            # Find other users with similar ratings - optimize with joins
            similar_users = {}
            
            # Get all other users' ratings in batch
            all_ratings = db.session.query(
                Rating.user_id,
                Rating.movie_id,
                Rating.rating
            ).filter(Rating.user_id != user_id).all()
            
            # Group by user
            other_users_ratings = {}
            for user_id_other, movie_id, rating_val in all_ratings:
                if user_id_other not in other_users_ratings:
                    other_users_ratings[user_id_other] = {}
                other_users_ratings[user_id_other][movie_id] = rating_val
            
            # Calculate similarity with other users
            for other_user_id, other_ratings_dict in other_users_ratings.items():
                other_rated_movies = set(other_ratings_dict.keys())
                
                # Calculate similarity (Jaccard similarity on common movies)
                common_movies = user_rated_movies.intersection(other_rated_movies)
                
                if not common_movies:
                    continue
                
                # Calculate correlation between ratings
                common_ratings_user = [user_ratings_dict[m] for m in common_movies]
                common_ratings_other = [other_ratings_dict[m] for m in common_movies]
                
                # Calculate Pearson correlation
                if len(common_ratings_user) >= 2:
                    try:
                        correlation = RecommendationService._calculate_pearson_correlation(
                            common_ratings_user,
                            common_ratings_other
                        )
                        if correlation >= min_similarity:
                            similar_users[other_user_id] = {
                                'correlation': correlation,
                                'rated_movies': other_rated_movies
                            }
                    except Exception as e:
                        logger.debug(f"Error calculating correlation for user {other_user_id}: {str(e)}")
                        continue
            
            if not similar_users:
                return []
            
            # Get movies recommended by similar users
            recommended_movies_scores = {}
            
            for other_user_id, data in similar_users.items():
                other_movies = data['rated_movies'] - user_rated_movies
                correlation = data['correlation']
                
                for movie_id in other_movies:
                    rating = other_users_ratings[other_user_id].get(movie_id)
                    if rating:
                        if movie_id not in recommended_movies_scores:
                            recommended_movies_scores[movie_id] = []
                        recommended_movies_scores[movie_id].append(rating * correlation)
            
            # Rank recommendations by weighted average rating
            ranked_movies = sorted(
                recommended_movies_scores.items(),
                key=lambda x: sum(x[1]) / len(x[1]),
                reverse=True
            )
            
            recommended_ids = [movie_id for movie_id, _ in ranked_movies[:limit]]
            if recommended_ids:
                recommendations = Movie.query.filter(Movie.id.in_(recommended_ids)).all()
                return recommendations
            return []
        except Exception as e:
            logger.error(f"Error getting collaborative filtering recommendations for user {user_id}: {str(e)}")
            return []
    
    @staticmethod
    def _calculate_pearson_correlation(x, y):
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0
        
        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
        denominator = (
            sum((x[i] - mean_x) ** 2 for i in range(len(x))) *
            sum((y[i] - mean_y) ** 2 for i in range(len(y)))
        ) ** 0.5
        
        if denominator == 0:
            return 0
        
        return numerator / denominator
    
    @staticmethod
    def get_combined_recommendations(user_id, limit=12):
        """
        Get combined recommendations from multiple algorithms.
        Blends genre-based, popularity-based, and collaborative filtering.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of recommendations
        
        Returns:
            List of Movie objects
        """
        # Get recommendations from different algorithms
        genre_recs = RecommendationService.get_genre_based_recommendations(user_id, limit)
        popularity_recs = RecommendationService.get_popularity_based_recommendations(user_id, limit)
        collab_recs = RecommendationService.get_collaborative_filtering_recommendations(user_id, limit)
        
        # Combine and deduplicate by movie ID, maintaining score
        rec_scores = {}
        
        for movie in genre_recs:
            rec_scores[movie.id] = rec_scores.get(movie.id, 0) + 3
        
        for movie in popularity_recs:
            rec_scores[movie.id] = rec_scores.get(movie.id, 0) + 2
        
        for movie in collab_recs:
            rec_scores[movie.id] = rec_scores.get(movie.id, 0) + 1
        
        # Sort by combined score
        sorted_movie_ids = sorted(rec_scores.keys(), key=lambda x: rec_scores[x], reverse=True)[:limit]
        
        # Get movies in sorted order
        recommendations = []
        for movie_id in sorted_movie_ids:
            movie = Movie.query.get(movie_id)
            if movie:
                recommendations.append(movie)
        
        return recommendations
