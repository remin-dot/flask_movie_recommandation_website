"""
Movie Recommendation Website - Main Flask Application
A full-stack web application for movie recommendations, ratings, and watchlists
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import or_, func, inspect, text
from datetime import datetime
import os
import json
import requests
from urllib.parse import quote_plus
from dotenv import load_dotenv
from models import db, User, Movie, Rating, Watchlist


load_dotenv()


# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_recommendation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JSON_SORT_KEYS'] = False

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'


KNOWN_POSTERS = {
    'the shawshank redemption': 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg',
    'the dark knight': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
    'inception': 'https://image.tmdb.org/t/p/w500/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg',
    'dune': 'https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg',
    'the grand budapest hotel': 'https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg',
    'parasite': 'https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg',
    'avatar': 'https://image.tmdb.org/t/p/w500/kyeqWdyUXW608qlYkRqosgbbJyK.jpg',
    'pulp fiction': 'https://image.tmdb.org/t/p/w500/vQWk5YBFWF4bZaofAbv0tShwBvQ.jpg',
    'forrest gump': 'https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg',
    'interstellar': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
}

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'th': 'ไทย',
    'zh': '中文',
    'ja': '日本語',
}

TRANSLATIONS = {
    'nav.home': {'en': 'Home', 'th': 'หน้าแรก', 'zh': '首页', 'ja': 'ホーム'},
    'nav.movies': {'en': 'Movies', 'th': 'ภาพยนตร์', 'zh': '电影', 'ja': '映画'},
    'nav.recommendations': {'en': 'Recommendations', 'th': 'แนะนำสำหรับคุณ', 'zh': '推荐', 'ja': 'おすすめ'},
    'nav.watchlist': {'en': 'Watchlist', 'th': 'รายการที่อยากดู', 'zh': '收藏清单', 'ja': 'ウォッチリスト'},
    'nav.add': {'en': 'Add', 'th': 'เพิ่ม', 'zh': '添加', 'ja': '追加'},
    'nav.dashboard': {'en': 'Dashboard', 'th': 'แดชบอร์ด', 'zh': '仪表盘', 'ja': 'ダッシュボード'},
    'nav.profile': {'en': 'Profile', 'th': 'โปรไฟล์', 'zh': '个人资料', 'ja': 'プロフィール'},
    'nav.logout': {'en': 'Logout', 'th': 'ออกจากระบบ', 'zh': '退出登录', 'ja': 'ログアウト'},
    'nav.login': {'en': 'Login', 'th': 'เข้าสู่ระบบ', 'zh': '登录', 'ja': 'ログイン'},
    'nav.register': {'en': 'Register', 'th': 'สมัครสมาชิก', 'zh': '注册', 'ja': '登録'},
    'search.placeholder': {
        'en': 'Search movies by title or genre...',
        'th': 'ค้นหาภาพยนตร์จากชื่อหรือประเภท...',
        'zh': '按片名或类型搜索电影...',
        'ja': 'タイトルまたはジャンルで映画を検索...'
    },
    'search.button': {'en': 'Search', 'th': 'ค้นหา', 'zh': '搜索', 'ja': '検索'},
    'footer.quick_links': {'en': 'Quick Links', 'th': 'ลิงก์ด่วน', 'zh': '快速链接', 'ja': 'クイックリンク'},
    'footer.contact': {'en': 'Contact & Info', 'th': 'ติดต่อและข้อมูล', 'zh': '联系与信息', 'ja': '連絡先・情報'},
    'movies.title': {'en': 'All Movies', 'th': 'ภาพยนตร์ทั้งหมด', 'zh': '所有电影', 'ja': 'すべての映画'},
    'movies.subtitle': {
        'en': 'Browse and discover movies from our collection',
        'th': 'เลือกดูและค้นพบภาพยนตร์จากคลังของเรา',
        'zh': '浏览并发现我们的电影收藏',
        'ja': 'コレクションから映画を見つけましょう'
    },
    'movies.view_details': {'en': 'View Details', 'th': 'ดูรายละเอียด', 'zh': '查看详情', 'ja': '詳細を見る'},
    'search.results': {'en': 'Search Results', 'th': 'ผลการค้นหา', 'zh': '搜索结果', 'ja': '検索結果'},
    'search.found_for': {'en': 'Found results for', 'th': 'ผลลัพธ์สำหรับ', 'zh': '搜索关键词', 'ja': '検索キーワード'},
    'home.featured': {'en': 'Featured Movies', 'th': 'ภาพยนตร์แนะนำ', 'zh': '精选电影', 'ja': '注目の映画'},
    'home.featured_sub': {'en': 'Handpicked movie selections just for you', 'th': 'คัดสรรหนังเด่นสำหรับคุณ', 'zh': '为你精选的电影推荐', 'ja': 'あなたのためのおすすめ作品'},
    'auth.welcome_back': {'en': 'Welcome Back', 'th': 'ยินดีต้อนรับกลับ', 'zh': '欢迎回来', 'ja': 'おかえりなさい'},
    'auth.signin_sub': {
        'en': 'Sign in to access your personalized movie recommendations',
        'th': 'เข้าสู่ระบบเพื่อดูคำแนะนำภาพยนตร์เฉพาะคุณ',
        'zh': '登录以查看为你定制的电影推荐',
        'ja': 'ログインしてあなた向けの映画おすすめを確認'
    },
    'auth.username': {'en': 'Username', 'th': 'ชื่อผู้ใช้', 'zh': '用户名', 'ja': 'ユーザー名'},
    'auth.password': {'en': 'Password', 'th': 'รหัสผ่าน', 'zh': '密码', 'ja': 'パスワード'},
    'auth.enter_username': {'en': 'Enter your username', 'th': 'กรอกชื่อผู้ใช้', 'zh': '输入用户名', 'ja': 'ユーザー名を入力'},
    'auth.enter_password': {'en': 'Enter your password', 'th': 'กรอกรหัสผ่าน', 'zh': '输入密码', 'ja': 'パスワードを入力'},
    'auth.signin': {'en': 'Sign In', 'th': 'เข้าสู่ระบบ', 'zh': '登录', 'ja': 'ログイン'},
    'auth.no_account': {'en': "Don't have an account?", 'th': 'ยังไม่มีบัญชีใช่ไหม?', 'zh': '还没有账号？', 'ja': 'アカウントをお持ちでないですか？'},
    'auth.create_now': {'en': 'Create one now', 'th': 'สร้างบัญชีเลย', 'zh': '立即创建', 'ja': '今すぐ作成'},
    'auth.join': {'en': 'Join FlickBase', 'th': 'เข้าร่วม FlickBase', 'zh': '加入 FlickBase', 'ja': 'FlickBaseに参加'},
    'auth.register_sub': {
        'en': 'Create an account and start discovering amazing movies',
        'th': 'สร้างบัญชีและเริ่มค้นพบภาพยนตร์ที่น่าสนใจ',
        'zh': '创建账号并开始探索精彩电影',
        'ja': 'アカウントを作成して素晴らしい映画を見つけよう'
    },
    'auth.email': {'en': 'Email Address', 'th': 'อีเมล', 'zh': '邮箱地址', 'ja': 'メールアドレス'},
    'auth.confirm_password': {'en': 'Confirm Password', 'th': 'ยืนยันรหัสผ่าน', 'zh': '确认密码', 'ja': 'パスワード確認'},
    'auth.choose_username': {'en': 'Choose a username', 'th': 'ตั้งชื่อผู้ใช้', 'zh': '设置用户名', 'ja': 'ユーザー名を設定'},
    'auth.enter_email': {'en': 'Enter your email', 'th': 'กรอกอีเมล', 'zh': '输入邮箱', 'ja': 'メールを入力'},
    'auth.create_password': {'en': 'Create a password', 'th': 'ตั้งรหัสผ่าน', 'zh': '创建密码', 'ja': 'パスワードを作成'},
    'auth.confirm_password_ph': {'en': 'Confirm your password', 'th': 'ยืนยันรหัสผ่านอีกครั้ง', 'zh': '再次输入密码', 'ja': 'パスワードを再入力'},
    'auth.create_account': {'en': 'Create Account', 'th': 'สร้างบัญชี', 'zh': '创建账号', 'ja': 'アカウント作成'},
    'auth.have_account': {'en': 'Already have an account?', 'th': 'มีบัญชีอยู่แล้ว?', 'zh': '已有账号？', 'ja': 'すでにアカウントがありますか？'},
    'auth.signin_here': {'en': 'Sign in here', 'th': 'เข้าสู่ระบบที่นี่', 'zh': '在此登录', 'ja': 'こちらからログイン'},
    'dashboard.welcome': {'en': 'Welcome', 'th': 'ยินดีต้อนรับ', 'zh': '欢迎', 'ja': 'ようこそ'},
    'dashboard.subtitle': {'en': "Here's your FlickBase dashboard", 'th': 'นี่คือแดชบอร์ด FlickBase ของคุณ', 'zh': '这是你的 FlickBase 仪表盘', 'ja': 'あなたのFlickBaseダッシュボードです'},
    'dashboard.movies_rated': {'en': 'Movies Rated', 'th': 'จำนวนหนังที่ให้คะแนน', 'zh': '已评分电影', 'ja': '評価した映画'},
    'dashboard.watchlist_items': {'en': 'Watchlist Items', 'th': 'รายการใน Watchlist', 'zh': '收藏数量', 'ja': 'ウォッチリスト件数'},
    'dashboard.avg_rating': {'en': 'Avg. Rating', 'th': 'คะแนนเฉลี่ย', 'zh': '平均评分', 'ja': '平均評価'},
    'dashboard.quick_actions': {'en': 'Quick Actions', 'th': 'เมนูด่วน', 'zh': '快捷操作', 'ja': 'クイック操作'},
    'dashboard.browse_movies': {'en': 'Browse Movies', 'th': 'ดูรายการหนัง', 'zh': '浏览电影', 'ja': '映画を探す'},
    'dashboard.get_recs': {'en': 'Get Recommendations', 'th': 'รับคำแนะนำ', 'zh': '获取推荐', 'ja': 'おすすめを見る'},
    'dashboard.add_movie': {'en': 'Add Movie', 'th': 'เพิ่มหนัง', 'zh': '添加电影', 'ja': '映画を追加'},
    'dashboard.view_watchlist': {'en': 'View Watchlist', 'th': 'ดู Watchlist', 'zh': '查看收藏', 'ja': 'ウォッチリストを見る'},
    'dashboard.high_rated': {'en': 'Your Highly Rated Movies', 'th': 'หนังที่คุณให้คะแนนสูง', 'zh': '你的高分电影', 'ja': '高評価した映画'},
    'dashboard.recent_ratings': {'en': 'Recent Ratings', 'th': 'คะแนนล่าสุด', 'zh': '最近评分', 'ja': '最近の評価'},
    'dashboard.start_rating': {'en': 'Start rating movies to see them here!', 'th': 'เริ่มให้คะแนนหนัง แล้วจะเห็นที่นี่!', 'zh': '先给电影评分，结果会显示在这里！', 'ja': '映画を評価するとここに表示されます！'},
    'common.movie': {'en': 'Movie', 'th': 'ภาพยนตร์', 'zh': '电影', 'ja': '映画'},
    'common.genre': {'en': 'Genre', 'th': 'ประเภท', 'zh': '类型', 'ja': 'ジャンル'},
    'common.year': {'en': 'Year', 'th': 'ปี', 'zh': '年份', 'ja': '年'},
    'common.rating': {'en': 'Rating', 'th': 'คะแนน', 'zh': '评分', 'ja': '評価'},
    'common.date': {'en': 'Date', 'th': 'วันที่', 'zh': '日期', 'ja': '日付'},
    'common.action': {'en': 'Action', 'th': 'การทำงาน', 'zh': '操作', 'ja': '操作'},
    'common.view': {'en': 'View', 'th': 'ดู', 'zh': '查看', 'ja': '見る'},
    'common.cancel': {'en': 'Cancel', 'th': 'ยกเลิก', 'zh': '取消', 'ja': 'キャンセル'},
    'pagination.previous': {'en': 'Previous', 'th': 'ก่อนหน้า', 'zh': '上一页', 'ja': '前へ'},
    'pagination.next': {'en': 'Next', 'th': 'ถัดไป', 'zh': '下一页', 'ja': '次へ'},
    'profile.title': {'en': 'My Profile', 'th': 'โปรไฟล์ของฉัน', 'zh': '我的资料', 'ja': 'マイプロフィール'},
    'profile.subtitle': {'en': 'Your movie rating history and statistics', 'th': 'ประวัติและสถิติการให้คะแนนของคุณ', 'zh': '你的评分历史与统计', 'ja': 'あなたの評価履歴と統計'},
    'profile.member_since': {'en': 'Member since', 'th': 'สมาชิกตั้งแต่', 'zh': '注册于', 'ja': '登録日'},
    'profile.total_ratings': {'en': 'Total Ratings', 'th': 'คะแนนทั้งหมด', 'zh': '总评分数', 'ja': '総評価数'},
    'profile.average_rating': {'en': 'Average Rating', 'th': 'คะแนนเฉลี่ย', 'zh': '平均评分', 'ja': '平均評価'},
    'profile.account_info': {'en': 'Account Information', 'th': 'ข้อมูลบัญชี', 'zh': '账户信息', 'ja': 'アカウント情報'},
    'profile.my_history': {'en': 'My Rating History', 'th': 'ประวัติการให้คะแนน', 'zh': '我的评分历史', 'ja': '評価履歴'},
    'profile.rating_distribution': {'en': 'Rating Distribution', 'th': 'การกระจายคะแนน', 'zh': '评分分布', 'ja': '評価分布'},
    'watchlist.title': {'en': 'My Watchlist', 'th': 'รายการที่อยากดูของฉัน', 'zh': '我的收藏清单', 'ja': 'マイウォッチリスト'},
    'watchlist.subtitle': {'en': 'Movies you want to watch', 'th': 'หนังที่คุณอยากดู', 'zh': '你想看的电影', 'ja': '見たい映画'},
    'watchlist.added': {'en': 'Added', 'th': 'เพิ่มเมื่อ', 'zh': '添加于', 'ja': '追加日'},
    'watchlist.remove': {'en': 'Remove', 'th': 'ลบออก', 'zh': '移除', 'ja': '削除'},
    'watchlist.empty_title': {'en': 'Your watchlist is empty!', 'th': 'Watchlist ของคุณว่างอยู่!', 'zh': '你的收藏清单为空！', 'ja': 'ウォッチリストは空です！'},
    'watchlist.empty_sub': {'en': 'Start adding movies to keep track of what you want to watch.', 'th': 'เริ่มเพิ่มหนังเพื่อบันทึกสิ่งที่อยากดู', 'zh': '开始添加电影以追踪你想看的内容', 'ja': '見たい映画を追加して管理しましょう'},
    'watchlist.empty_link': {'en': 'Browse movies and add them to your watchlist', 'th': 'ดูหนังแล้วเพิ่มเข้า watchlist', 'zh': '浏览电影并加入收藏', 'ja': '映画を探してウォッチリストに追加'},
    'recs.title': {'en': 'Personalized Recommendations', 'th': 'คำแนะนำเฉพาะคุณ', 'zh': '个性化推荐', 'ja': 'あなた向けのおすすめ'},
    'recs.none_title': {'en': 'No recommendations yet!', 'th': 'ยังไม่มีคำแนะนำ', 'zh': '暂无推荐！', 'ja': 'まだおすすめがありません'},
    'recs.none_sub': {'en': 'To get personalized recommendations, you need to rate movies with 4 or 5 stars.', 'th': 'หากต้องการคำแนะนำเฉพาะตัว ให้ให้คะแนนหนัง 4 หรือ 5 ดาว', 'zh': '要获得个性化推荐，请先给电影打4或5星', 'ja': '4〜5星で評価するとおすすめが表示されます'},
    'recs.how_title': {'en': 'How Recommendations Work', 'th': 'ระบบแนะนำทำงานอย่างไร', 'zh': '推荐机制说明', 'ja': 'おすすめの仕組み'},
    'add.title': {'en': 'Add a New Movie', 'th': 'เพิ่มภาพยนตร์ใหม่', 'zh': '添加新电影', 'ja': '新しい映画を追加'},
    'add.movie_title': {'en': 'Movie Title', 'th': 'ชื่อภาพยนตร์', 'zh': '电影标题', 'ja': '映画タイトル'},
    'add.release_year': {'en': 'Release Year', 'th': 'ปีที่ฉาย', 'zh': '上映年份', 'ja': '公開年'},
    'add.description': {'en': 'Description', 'th': 'คำอธิบาย', 'zh': '简介', 'ja': '説明'},
    'add.tip': {'en': "Tip: Make sure the movie doesn't already exist in our database before adding it.", 'th': 'เคล็ดลับ: ตรวจสอบก่อนว่าในฐานข้อมูลยังไม่มีหนังเรื่องนี้', 'zh': '提示：添加前请确认数据库中尚无该电影', 'ja': 'ヒント: 追加前に既存データを確認してください'},
    'rate.title': {'en': 'Rate', 'th': 'ให้คะแนน', 'zh': '评分', 'ja': '評価する'},
    'rate.your_rating': {'en': 'Your Rating', 'th': 'คะแนนของคุณ', 'zh': '你的评分', 'ja': 'あなたの評価'},
    'rate.review': {'en': 'Your Review (Optional)', 'th': 'รีวิวของคุณ (ไม่บังคับ)', 'zh': '你的评论（可选）', 'ja': 'レビュー（任意）'},
    'rate.save': {'en': 'Save Rating', 'th': 'บันทึกคะแนน', 'zh': '保存评分', 'ja': '評価を保存'},
    'rate.update': {'en': 'Update Rating', 'th': 'อัปเดตคะแนน', 'zh': '更新评分', 'ja': '評価を更新'},
    'detail.plot': {'en': 'Plot', 'th': 'เรื่องย่อ', 'zh': '剧情简介', 'ja': 'あらすじ'},
    'detail.community': {'en': 'Community Rating', 'th': 'คะแนนจากผู้ชม', 'zh': '社区评分', 'ja': 'コミュニティ評価'},
    'footer.desc': {
        'en': 'Discover, rate, and share your favorite movies with our community.',
        'th': 'ค้นหา ให้คะแนน และแชร์หนังเรื่องโปรดกับชุมชนของเรา',
        'zh': '与社区一起发现、评分并分享你喜爱的电影。',
        'ja': 'お気に入りの映画を見つけ、評価し、コミュニティと共有しましょう。'
    },
    'flash.all_fields_required': {'en': 'All fields are required.', 'th': 'กรุณากรอกข้อมูลให้ครบทุกช่อง', 'zh': '请填写所有字段。', 'ja': 'すべての項目を入力してください。'},
    'flash.passwords_no_match': {'en': 'Passwords do not match.', 'th': 'รหัสผ่านไม่ตรงกัน', 'zh': '两次输入的密码不一致。', 'ja': 'パスワードが一致しません。'},
    'flash.username_exists': {'en': 'Username already exists.', 'th': 'ชื่อผู้ใช้นี้ถูกใช้แล้ว', 'zh': '用户名已存在。', 'ja': 'ユーザー名は既に存在します。'},
    'flash.email_exists': {'en': 'Email already registered.', 'th': 'อีเมลนี้ถูกลงทะเบียนแล้ว', 'zh': '邮箱已被注册。', 'ja': 'メールアドレスは既に登録されています。'},
    'flash.register_success': {'en': 'Registration successful! Please log in.', 'th': 'สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ', 'zh': '注册成功！请登录。', 'ja': '登録に成功しました。ログインしてください。'},
    'flash.invalid_login': {'en': 'Invalid username or password.', 'th': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'zh': '用户名或密码错误。', 'ja': 'ユーザー名またはパスワードが正しくありません。'},
    'flash.welcome_back': {'en': 'Welcome back, {username}!', 'th': 'ยินดีต้อนรับกลับ, {username}!', 'zh': '欢迎回来，{username}！', 'ja': 'おかえりなさい、{username}さん！'},
    'flash.logged_out': {'en': 'You have been logged out.', 'th': 'คุณออกจากระบบแล้ว', 'zh': '你已退出登录。', 'ja': 'ログアウトしました。'},
    'flash.invalid_year': {'en': 'Please enter a valid year.', 'th': 'กรุณากรอกปีที่ถูกต้อง', 'zh': '请输入有效年份。', 'ja': '有効な年を入力してください。'},
    'flash.year_number': {'en': 'Year must be a number.', 'th': 'ปีต้องเป็นตัวเลข', 'zh': '年份必须是数字。', 'ja': '年は数字で入力してください。'},
    'flash.movie_exists': {'en': 'This movie already exists in the database.', 'th': 'มีหนังเรื่องนี้ในฐานข้อมูลแล้ว', 'zh': '该电影已存在于数据库中。', 'ja': 'この映画は既にデータベースに存在します。'},
    'flash.movie_added': {'en': 'Movie "{title}" added successfully!', 'th': 'เพิ่มหนัง "{title}" สำเร็จ!', 'zh': '电影“{title}”添加成功！', 'ja': '映画「{title}」を追加しました。'},
    'flash.rating_range': {'en': 'Please provide a rating between 1 and 5.', 'th': 'กรุณาให้คะแนนระหว่าง 1 ถึง 5', 'zh': '评分必须在1到5之间。', 'ja': '評価は1〜5の範囲で入力してください。'},
    'flash.rating_updated': {'en': 'Your rating has been updated.', 'th': 'อัปเดตคะแนนของคุณแล้ว', 'zh': '你的评分已更新。', 'ja': '評価を更新しました。'},
    'flash.rating_saved': {'en': 'Your rating has been saved.', 'th': 'บันทึกคะแนนของคุณแล้ว', 'zh': '你的评分已保存。', 'ja': '評価を保存しました。'},
    'flash.no_permission': {'en': 'You do not have permission to delete this rating.', 'th': 'คุณไม่มีสิทธิ์ลบคะแนนนี้', 'zh': '你无权删除该评分。', 'ja': 'この評価を削除する権限がありません。'},
    'flash.rating_deleted': {'en': 'Your rating has been deleted.', 'th': 'ลบคะแนนของคุณแล้ว', 'zh': '你的评分已删除。', 'ja': '評価を削除しました。'},
    'flash.rate_for_recs': {'en': 'Rate some movies to get personalized recommendations!', 'th': 'ให้คะแนนหนังสักหน่อย เพื่อรับคำแนะนำเฉพาะคุณ!', 'zh': '请先给一些电影评分以获得个性化推荐！', 'ja': '映画を評価するとおすすめが表示されます！'},
    'flash.search_min': {'en': 'Please enter at least 2 characters to search.', 'th': 'กรุณาพิมพ์อย่างน้อย 2 ตัวอักษรเพื่อค้นหา', 'zh': '请至少输入2个字符进行搜索。', 'ja': '検索するには2文字以上入力してください。'},
    'msg.no_recs': {'en': 'No recommendations yet.', 'th': 'ยังไม่มีคำแนะนำ', 'zh': '暂无推荐。', 'ja': 'まだおすすめはありません。'},
    'msg.recs_based_on': {'en': 'Recommendations based on your interest in: {genres}', 'th': 'คำแนะนำจากความสนใจของคุณในหมวด: {genres}', 'zh': '基于你对以下类型的兴趣推荐：{genres}', 'ja': '次のジャンルの好みに基づくおすすめ: {genres}'},
    'errors.404_title': {'en': 'Page Not Found', 'th': 'ไม่พบหน้าที่ต้องการ', 'zh': '页面未找到', 'ja': 'ページが見つかりません'},
    'errors.404_text': {'en': "Sorry, the page you're looking for doesn't exist or has been moved.", 'th': 'ขออภัย ไม่พบหน้าที่คุณต้องการ หรืออาจถูกย้ายตำแหน่งแล้ว', 'zh': '抱歉，你访问的页面不存在或已被移动。', 'ja': 'お探しのページは存在しないか移動されました。'},
    'errors.500_title': {'en': 'Server Error', 'th': 'เซิร์ฟเวอร์ขัดข้อง', 'zh': '服务器错误', 'ja': 'サーバーエラー'},
    'errors.500_text': {'en': 'Oops! Something went wrong on our end. Our team has been notified.', 'th': 'ขออภัย ระบบเกิดข้อผิดพลาด ทีมงานได้รับการแจ้งเตือนแล้ว', 'zh': '糟糕！服务器出现问题，团队已收到通知。', 'ja': 'エラーが発生しました。運営チームへ通知済みです。'},
    'errors.go_home': {'en': 'Go to Home', 'th': 'กลับหน้าแรก', 'zh': '返回首页', 'ja': 'ホームへ戻る'},
    'errors.go_back': {'en': 'Go Back', 'th': 'ย้อนกลับ', 'zh': '返回上一页', 'ja': '戻る'},
}

MOVIE_CATALOG = [
    {
        'title': 'The Shawshank Redemption',
        'genre': 'Drama',
        'year': 1994,
        'description': 'Wrongfully convicted banker Andy Dufresne begins a life sentence at Shawshank Prison, where he forges an enduring friendship with Red, learns to survive a brutal system, and quietly pursues hope through patience, intellect, and small acts of humanity that slowly transform everyone around him.'
    },
    {
        'title': 'The Dark Knight',
        'genre': 'Action',
        'year': 2008,
        'description': 'As Gotham starts to believe in law and order, Batman, Commissioner Gordon, and Harvey Dent face the Joker, a chaotic mastermind who weaponizes fear and moral compromise, forcing heroes and citizens alike to choose between security, truth, and the cost of becoming what they fight.'
    },
    {
        'title': 'Inception',
        'genre': 'Sci-Fi',
        'year': 2010,
        'description': 'Dom Cobb leads a team of specialists who infiltrate layered dream worlds to steal secrets, but a final mission demands planting an idea instead, pulling him into a dangerous psychological maze where memory, guilt, and reality blur with every deeper level of sleep.'
    },
    {
        'title': 'Dune',
        'genre': 'Sci-Fi',
        'year': 2021,
        'description': 'On the desert world of Arrakis, Paul Atreides inherits a destiny tied to politics, prophecy, and survival after his noble family is betrayed, and he must learn the culture of the Fremen while confronting visions that suggest he could become either liberator or destroyer.'
    },
    {
        'title': 'The Grand Budapest Hotel',
        'genre': 'Comedy',
        'year': 2014,
        'description': 'Legendary concierge Monsieur Gustave and his loyal protégé Zero navigate theft, war, and shifting social class in a beautifully stylized European hotel, turning a murder mystery into a bittersweet tale about friendship, memory, and a vanished world.'
    },
    {
        'title': 'Parasite',
        'genre': 'Drama',
        'year': 2019,
        'description': 'A struggling family gradually infiltrates the household of a wealthy clan through deception and performance, but as class resentment, hidden spaces, and desperate survival collide, their carefully staged ascent erupts into tragedy.'
    },
    {
        'title': 'Avatar',
        'genre': 'Sci-Fi',
        'year': 2009,
        'description': 'Marine veteran Jake Sully enters the body of an alien avatar on Pandora and is drawn into the Na’vi world, where love, ecology, and colonial violence clash as he decides whether to obey orders or defend a planet and people under threat.'
    },
    {
        'title': 'Pulp Fiction',
        'genre': 'Crime',
        'year': 1994,
        'description': 'Interwoven stories of hitmen, a boxer, and a mob boss unfold in nonlinear chapters full of dark humor, sudden violence, and pop-culture dialogue, revealing how chance encounters can radically alter the fate of criminals and bystanders alike.'
    },
    {
        'title': 'Forrest Gump',
        'genre': 'Drama',
        'year': 1994,
        'description': 'Through innocence, persistence, and kindness, Forrest unexpectedly intersects with defining moments of modern American history while searching for the love of his life, proving that a simple life can still hold extraordinary meaning.'
    },
    {
        'title': 'Interstellar',
        'genre': 'Sci-Fi',
        'year': 2014,
        'description': 'When Earth nears ecological collapse, a former pilot joins a mission through a wormhole in search of habitable worlds, confronting relativistic time, impossible choices, and the emotional gravity of leaving family behind to save humanity.'
    },
    {'title': 'The Matrix', 'genre': 'Sci-Fi', 'year': 1999, 'description': 'Computer hacker Neo discovers reality is a simulated prison built by machines, and with a rebel crew he learns to bend its rules, confronting identity, control, and destiny in a cyberpunk war for human freedom.'},
    {'title': 'Gladiator', 'genre': 'Action', 'year': 2000, 'description': 'Roman general Maximus is betrayed, enslaved, and forced into the arena, where his rise as a gladiator becomes a path toward revenge, justice, and the restoration of honor in an empire corrupted by ambition.'},
    {'title': 'Titanic', 'genre': 'Drama', 'year': 1997, 'description': 'A romance between Jack and Rose blooms across class boundaries aboard the RMS Titanic, and when disaster strikes, their love story becomes a haunting portrait of courage, loss, and fleeting human connection.'},
    {'title': 'The Godfather', 'genre': 'Crime', 'year': 1972, 'description': 'As the Corleone family navigates violence, loyalty, and political influence, reluctant son Michael is drawn deeper into organized crime, transforming from outsider to calculating patriarch in a saga about power and family legacy.'},
    {'title': 'The Godfather Part II', 'genre': 'Crime', 'year': 1974, 'description': 'Parallel narratives follow young Vito Corleone’s rise and Michael’s cold consolidation of power, revealing how ambition and mistrust can preserve an empire while destroying the very relationships meant to sustain it.'},
    {'title': 'The Lord of the Rings: The Fellowship of the Ring', 'genre': 'Fantasy', 'year': 2001, 'description': 'Frodo Baggins leaves the safety of the Shire with a diverse fellowship to destroy an ancient ring of power, beginning an epic journey of friendship, sacrifice, and resistance against gathering darkness.'},
    {'title': 'The Lord of the Rings: The Two Towers', 'genre': 'Fantasy', 'year': 2002, 'description': 'Separated companions fight on multiple fronts as kingdoms fall and alliances are tested, while Frodo and Sam move closer to Mordor under the dangerous guidance of Gollum.'},
    {'title': 'The Lord of the Rings: The Return of the King', 'genre': 'Fantasy', 'year': 2003, 'description': 'As armies march on Minas Tirith and hope narrows to a single impossible mission, the final battle for Middle-earth asks whether mercy, loyalty, and endurance can overcome absolute power.'},
    {'title': 'Fight Club', 'genre': 'Drama', 'year': 1999, 'description': 'An insomniac office worker forms an intense friendship with the charismatic Tyler Durden, leading to an underground fight movement that evolves into anarchic rebellion and a disturbing confrontation with fractured identity.'},
    {'title': 'Whiplash', 'genre': 'Drama', 'year': 2014, 'description': 'Driven drummer Andrew Neiman enters an elite jazz program under a ruthless instructor whose psychological pressure pushes him toward technical brilliance, obsession, and the dangerous line between discipline and abuse.'},
    {'title': 'La La Land', 'genre': 'Romance', 'year': 2016, 'description': 'In Los Angeles, a pianist and an aspiring actress fall in love while pursuing artistic dreams, discovering that timing, ambition, and compromise can turn a joyful romance into a bittersweet memory.'},
    {'title': 'Spirited Away', 'genre': 'Animation', 'year': 2001, 'description': 'Young Chihiro enters a mysterious spirit world to save her transformed parents, and through courage and compassion she matures in a surreal coming-of-age journey filled with wonder, danger, and unforgettable creatures.'},
    {'title': 'Your Name', 'genre': 'Animation', 'year': 2016, 'description': 'Two teenagers inexplicably swap bodies across distance and time, forming a fragile bond through notes and routines before a cosmic twist reveals a race against memory and fate.'},
    {'title': 'The Silence of the Lambs', 'genre': 'Thriller', 'year': 1991, 'description': 'FBI trainee Clarice Starling seeks insights from imprisoned psychiatrist Hannibal Lecter to catch a serial killer, entering a tense psychological duel where intelligence and vulnerability become survival tools.'},
    {'title': 'Se7en', 'genre': 'Thriller', 'year': 1995, 'description': 'Two detectives investigate a series of murders inspired by the seven deadly sins, descending through a rain-soaked city where moral decay and personal trauma culminate in a devastating final revelation.'},
    {'title': 'Mad Max: Fury Road', 'genre': 'Action', 'year': 2015, 'description': 'In a post-apocalyptic wasteland, Max joins Furiosa in a high-octane escape from a tyrant’s army, turning a relentless chase into a rebellion for autonomy, dignity, and survival.'},
    {'title': 'Coco', 'genre': 'Animation', 'year': 2017, 'description': 'Young Miguel travels to the Land of the Dead to uncover his family’s hidden history, learning that remembrance, truth, and forgiveness can heal generations.'},
    {'title': 'The Prestige', 'genre': 'Mystery', 'year': 2006, 'description': 'Two rival magicians in Victorian London escalate their obsession with outdoing each other, sacrificing ethics, relationships, and sanity in pursuit of the ultimate illusion.'},
    {'title': 'Blade Runner 2049', 'genre': 'Sci-Fi', 'year': 2017, 'description': 'A replicant blade runner uncovers evidence that could destabilize society, sending him through haunting landscapes and buried memories to confront what it means to be real and worthy of life.'},
    {'title': 'Arrival', 'genre': 'Sci-Fi', 'year': 2016, 'description': 'A linguist is recruited to communicate with mysterious alien visitors, and as she deciphers their language she experiences time itself differently, forcing profound choices about love and loss.'},
    {'title': 'The Social Network', 'genre': 'Drama', 'year': 2010, 'description': 'The rise of a social media empire is told through lawsuits and betrayals, revealing how brilliance, insecurity, and ambition can create global influence while fracturing personal trust.'},
]

GENRE_ROTATION = [
    'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Drama', 'Fantasy',
    'Horror', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'Documentary'
]

TITLE_PREFIXES = [
    'Crimson', 'Silver', 'Golden', 'Midnight', 'Endless', 'Hidden', 'Radiant',
    'Broken', 'Silent', 'Fallen', 'Rising', 'Frozen', 'Burning', 'Neon',
    'Forgotten', 'Shattered', 'Emerald', 'Scarlet', 'Obsidian', 'Lunar',
    'Solar', 'Violet', 'Ancient', 'Modern', 'Last'
]

TITLE_TOPICS = [
    'Legacy', 'Horizon', 'Echo', 'Labyrinth', 'Promise', 'Requiem', 'Frontier',
    'Chronicle', 'Voyage', 'Signal', 'Paradox', 'Memory', 'Kingdom', 'Cipher',
    'Alliance', 'Sanctuary', 'Rebellion', 'Odyssey', 'Mirage', 'Awakening'
]

TMDB_BASE_URL = os.environ.get('TMDB_BASE_URL', 'https://api.themoviedb.org/3')
TMDB_IMAGE_BASE_URL = os.environ.get('TMDB_IMAGE_BASE_URL', 'https://image.tmdb.org/t/p/w500')

STREAMING_PLATFORM_ALIASES = {
    'netflix': ['Netflix'],
    'disney_plus': ['Disney Plus', 'Disney+'],
    'iqiyi': ['iQIYI', 'IQIYI', 'iQiyi'],
    'viu': ['Viu', 'VIU'],
}

STREAMING_FALLBACK_LABELS = ['Netflix', 'Disney+', 'iQIYI', 'VIU']

GENRE_ID_MAP = {
    28: 'Action',
    12: 'Adventure',
    16: 'Animation',
    35: 'Comedy',
    80: 'Crime',
    99: 'Documentary',
    18: 'Drama',
    14: 'Fantasy',
    27: 'Horror',
    9648: 'Mystery',
    10749: 'Romance',
    878: 'Sci-Fi',
    53: 'Thriller',
}


def build_generated_movie_catalog(target_count=500):
    """Build catalog entries to reach approximately target_count movies."""
    entries = list(MOVIE_CATALOG)
    existing_keys = {(item['title'].strip().lower(), item['year']) for item in entries}

    index = 0
    while len(entries) < target_count:
        prefix = TITLE_PREFIXES[index % len(TITLE_PREFIXES)]
        topic = TITLE_TOPICS[(index // len(TITLE_PREFIXES)) % len(TITLE_TOPICS)]
        title = f"{prefix} {topic} {index + 1:03d}"
        year = 1980 + ((index * 3) % 45)
        genre = GENRE_ROTATION[index % len(GENRE_ROTATION)]
        key = (title.lower(), year)

        if key not in existing_keys:
            entries.append({
                'title': title,
                'genre': genre,
                'year': year,
                'description': (
                    f"{title} follows a group of conflicted characters navigating a {genre.lower()}-driven world shaped by political tension, personal loyalty, and moral compromise. "
                    f"As events in {year} escalate, the story moves from intimate decisions to high-stakes consequences, blending emotional depth with suspenseful momentum and a memorable final turn."
                )
            })
            existing_keys.add(key)
        index += 1

    return entries


def get_tmdb_api_key():
    """Get TMDB API key from env."""
    return os.environ.get('TMDB_API_KEY', '').strip()


def tmdb_get(endpoint, params=None):
    """Execute TMDB GET request with API key."""
    api_key = get_tmdb_api_key()
    if not api_key:
        return None

    query = dict(params or {})
    query['api_key'] = api_key

    try:
        response = requests.get(f"{TMDB_BASE_URL}{endpoint}", params=query, timeout=12)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def find_provider_ids(region='TH'):
    """Find provider IDs from TMDB by provider names per region."""
    data = tmdb_get('/watch/providers/movie', {'watch_region': region, 'language': 'en-US'})
    if not data:
        return {}

    providers = data.get('results', [])
    found = {}

    for platform_key, aliases in STREAMING_PLATFORM_ALIASES.items():
        alias_set = {alias.lower() for alias in aliases}
        provider = next((item for item in providers if (item.get('provider_name') or '').lower() in alias_set), None)
        if provider:
            found[platform_key] = {
                'id': provider.get('provider_id'),
                'name': provider.get('provider_name')
            }

    return found


def normalize_genre_from_tmdb(genre_ids):
    """Map TMDB genre IDs to local genre string."""
    for genre_id in genre_ids or []:
        if genre_id in GENRE_ID_MAP:
            return GENRE_ID_MAP[genre_id]
    return 'Drama'


def build_entry_from_tmdb(movie_data, provider_name):
    """Build local movie entry from TMDB record."""
    title = (movie_data.get('title') or '').strip()
    release_date = movie_data.get('release_date') or ''
    year = int(release_date[:4]) if len(release_date) >= 4 and release_date[:4].isdigit() else 2000
    overview = (movie_data.get('overview') or '').strip()

    if not title:
        return None

    if not overview:
        overview = (
            f"{title} is a feature film available via {provider_name}, presented with dramatic stakes, evolving character motivations, "
            f"and a cinematic journey that builds toward an emotional and memorable final act."
        )

    poster_path = movie_data.get('poster_path')
    poster_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None

    return {
        'title': title,
        'genre': normalize_genre_from_tmdb(movie_data.get('genre_ids', [])),
        'year': year,
        'description': overview,
        'poster_url': poster_url,
    }


def import_streaming_catalog(region='TH', pages_per_provider=5):
    """Import movies available on Netflix/Disney+/iQIYI/VIU from TMDB."""
    if not get_tmdb_api_key():
        return import_streaming_catalog_fallback()

    provider_map = find_provider_ids(region=region)
    if not provider_map:
        return {'imported': 0, 'updated': 0, 'providers_found': 0, 'tmdb_enabled': True, 'fallback_mode': False}

    imported = 0
    updated = 0

    for platform_key, provider in provider_map.items():
        provider_id = provider.get('id')
        provider_name = provider.get('name') or platform_key

        for page in range(1, max(1, pages_per_provider) + 1):
            data = tmdb_get('/discover/movie', {
                'watch_region': region,
                'with_watch_providers': provider_id,
                'sort_by': 'popularity.desc',
                'language': 'en-US',
                'include_adult': 'false',
                'page': page,
            })

            if not data:
                break

            for item in data.get('results', []):
                entry = build_entry_from_tmdb(item, provider_name)
                if not entry:
                    continue

                existing = Movie.query.filter_by(title=entry['title'], year=entry['year']).first()
                payload = build_multilang_description(
                    entry['title'],
                    entry['genre'],
                    entry['year'],
                    entry['description']
                )

                if existing:
                    changed = False
                    if (not existing.description) or len(read_multilang_description(existing.description, 'en')) < len(entry['description']):
                        existing.description = payload
                        changed = True
                    if not existing.poster_url and entry.get('poster_url'):
                        existing.poster_url = entry['poster_url']
                        changed = True
                    if changed:
                        updated += 1
                else:
                    movie = Movie(
                        title=entry['title'],
                        genre=entry['genre'],
                        year=entry['year'],
                        description=payload,
                        poster_url=entry.get('poster_url') or get_poster_for_movie(entry['title'], entry['year'])
                    )
                    db.session.add(movie)
                    imported += 1

    if imported or updated:
        db.session.commit()

    return {
        'imported': imported,
        'updated': updated,
        'providers_found': len(provider_map),
        'tmdb_enabled': True,
        'fallback_mode': False,
    }


def build_multilang_description(title, genre, year, en_description):
    """Create multilingual description payload for one movie."""
    en_text = en_description.strip()
    th_text = (
        f"{title} เป็นภาพยนตร์แนว {genre} ที่เล่าเรื่องตัวละครหลายมิติท่ามกลางความขัดแย้งทางสังคมและอารมณ์ส่วนตัวอย่างเข้มข้น "
        f"เหตุการณ์ในปี {year} ค่อยๆ ขยายจากปัญหาเล็กๆ ไปสู่จุดเปลี่ยนสำคัญ พร้อมบรรยากาศที่ชวนติดตามและบทสรุปที่น่าจดจำ."
    )
    zh_text = (
        f"《{title}》是一部{genre}题材电影，围绕复杂人物在社会压力与个人选择中的挣扎展开。"
        f"故事以{year}年的关键事件为线索，逐步从细节冲突推进到高强度高潮，并以富有余韵的结尾收束全片。"
    )
    ja_text = (
        f"『{title}』は{genre}を軸に、人間関係と価値観の衝突を丁寧に描く作品です。"
        f"{year}年を背景に、静かな葛藤がやがて大きな転機へとつながり、感情の余韻を残すラストへ到達します。"
    )

    return json.dumps(
        {'en': en_text, 'th': th_text, 'zh': zh_text, 'ja': ja_text},
        ensure_ascii=False
    )


def read_multilang_description(raw_description, lang_code):
    """Read selected language from description payload or return plain text."""
    if not raw_description:
        return ''

    text = raw_description.strip()
    if text.startswith('{') and text.endswith('}'):
        try:
            payload = json.loads(text)
            if isinstance(payload, dict):
                return payload.get(lang_code) or payload.get('en') or next(iter(payload.values()), '')
        except json.JSONDecodeError:
            return raw_description

    return raw_description


def parse_description_payload(raw_description):
    """Parse multilingual JSON description payload or wrap plain text."""
    if not raw_description:
        return {'en': '', 'th': '', 'zh': '', 'ja': ''}

    text_value = raw_description.strip()
    if text_value.startswith('{') and text_value.endswith('}'):
        try:
            payload = json.loads(text_value)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass

    return {
        'en': raw_description,
        'th': raw_description,
        'zh': raw_description,
        'ja': raw_description,
    }


def append_provider_note(payload, provider_name):
    """Append localized provider note into multilingual description payload."""
    suffixes = {
        'en': f"\n\nStreaming Provider: {provider_name} (sample dataset; unverified availability)",
        'th': f"\n\nผู้ให้บริการสตรีมมิง: {provider_name} (ข้อมูลตัวอย่าง ยังไม่ยืนยันสิทธิ์การรับชม)",
        'zh': f"\n\n流媒体平台：{provider_name}（示例数据，未验证可用性）",
        'ja': f"\n\n配信プラットフォーム: {provider_name}（サンプルデータ・配信可否未確認）",
    }

    for lang_code, suffix in suffixes.items():
        base = payload.get(lang_code) or payload.get('en') or ''
        if suffix not in base:
            payload[lang_code] = f"{base}{suffix}".strip()

    return payload


def import_streaming_catalog_fallback():
    """Fallback assignment when TMDB key is unavailable."""
    movies = Movie.query.order_by(Movie.id.asc()).all()
    updated = 0

    for index, movie in enumerate(movies):
        provider_name = STREAMING_FALLBACK_LABELS[index % len(STREAMING_FALLBACK_LABELS)]
        payload = parse_description_payload(movie.description)
        payload = append_provider_note(payload, provider_name)
        serialized = json.dumps(payload, ensure_ascii=False)
        if movie.description != serialized:
            movie.description = serialized
            updated += 1

    if updated:
        db.session.commit()

    return {
        'imported': 0,
        'updated': updated,
        'providers_found': len(STREAMING_FALLBACK_LABELS),
        'tmdb_enabled': False,
        'fallback_mode': True,
    }


def get_current_language():
    """Get the active UI language code."""
    selected = session.get('lang', 'en')
    return selected if selected in SUPPORTED_LANGUAGES else 'en'


def translate_key(key, lang=None):
    """Translate a UI key to selected language."""
    current_lang = lang or get_current_language()
    entry = TRANSLATIONS.get(key, {})
    return entry.get(current_lang) or entry.get('en') or key


def tf(key, **kwargs):
    """Translate and format messages with variables."""
    text_value = translate_key(key)
    try:
        return text_value.format(**kwargs)
    except Exception:
        return text_value


@app.context_processor
def inject_i18n():
    """Expose translation helpers to templates."""
    lang = get_current_language()
    return {
        't': translate_key,
        'current_lang': lang,
        'supported_languages': SUPPORTED_LANGUAGES,
        'movie_desc': get_movie_description,
    }


def get_movie_description(movie, max_len=None):
    """Return localized movie description for active language."""
    current_lang = get_current_language()
    description = read_multilang_description(movie.description, current_lang)
    if max_len and len(description) > max_len:
        return f"{description[:max_len].rstrip()}..."
    return description


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


# ==================== Database Initialization ====================

def init_db():
    """Initialize database and add sample data"""
    with app.app_context():
        db.create_all()
        ensure_movie_schema()
        seed_or_update_movie_catalog()
        streaming_result = import_streaming_catalog(
            region=os.environ.get('STREAMING_REGION', 'TH'),
            pages_per_provider=int(os.environ.get('STREAMING_MAX_PAGES', '2'))
        )
        if streaming_result.get('fallback_mode'):
            print(
                f"[streaming:fallback] providers={streaming_result.get('providers_found', 0)} "
                f"updated={streaming_result.get('updated', 0)}"
            )
        elif streaming_result.get('tmdb_enabled'):
            print(
                f"[streaming] providers={streaming_result.get('providers_found', 0)} "
                f"imported={streaming_result.get('imported', 0)} updated={streaming_result.get('updated', 0)}"
            )
        removed = remove_duplicate_movies()
        if removed:
            print(f"[movies] removed duplicate movies: {removed}")
        sync_movie_posters()
        
        # Check if database already has data
        if User.query.first() is not None:
            return


def seed_or_update_movie_catalog():
    """Seed many movies and update short descriptions to longer ones."""
    changed = 0

    full_catalog = build_generated_movie_catalog(target_count=500)

    for entry in full_catalog:
        existing = Movie.query.filter_by(title=entry['title'], year=entry['year']).first()
        description_payload = build_multilang_description(
            entry['title'],
            entry['genre'],
            entry['year'],
            entry['description']
        )

        if existing:
            current_en = read_multilang_description(existing.description, 'en')
            if not current_en or len(current_en.strip()) < len(entry['description'].strip()):
                existing.description = description_payload
                changed += 1
            elif existing.description and not existing.description.strip().startswith('{'):
                existing.description = description_payload
                changed += 1

            if not existing.poster_url:
                existing.poster_url = get_poster_for_movie(entry['title'], entry['year'])
                changed += 1

            if not existing.genre and entry.get('genre'):
                existing.genre = entry['genre']
                changed += 1
            continue

        movie = Movie(
            title=entry['title'],
            genre=entry['genre'],
            year=entry['year'],
            description=description_payload,
            poster_url=get_poster_for_movie(entry['title'], entry['year'])
        )
        db.session.add(movie)
        changed += 1

    if changed:
        db.session.commit()
        print(f"[movies] seeded/updated catalog rows: {changed}")


def ensure_movie_schema():
    """Ensure legacy databases include poster_url column"""
    inspector = inspect(db.engine)
    movie_columns = {column['name'] for column in inspector.get_columns('movies')}

    if 'poster_url' not in movie_columns:
        db.session.execute(text('ALTER TABLE movies ADD COLUMN poster_url VARCHAR(500)'))
        db.session.commit()


def build_unique_placeholder(title, year, unique_suffix=None):
    """Build a deterministic fallback poster URL unique to a movie"""
    suffix = f" #{unique_suffix}" if unique_suffix is not None else ""
    label = quote_plus(f"{title} ({year}){suffix}")
    return f"https://placehold.co/500x750/1f2937/f8fafc?text={label}"


def get_poster_for_movie(title, year):
    """Get movie poster URL from known set or fallback"""
    normalized_title = (title or '').strip().lower()
    known_poster = KNOWN_POSTERS.get(normalized_title)
    if known_poster:
        return known_poster
    return build_unique_placeholder(title, year)


def sync_movie_posters():
    """Assign per-movie posters and fix duplicates"""
    movies = Movie.query.all()
    changed = 0

    for movie in movies:
        expected_poster = get_poster_for_movie(movie.title, movie.year)
        if not movie.poster_url:
            movie.poster_url = expected_poster
            changed += 1

    seen_urls = {}
    duplicate_fixes = 0
    for movie in movies:
        url = (movie.poster_url or '').strip()
        if not url:
            movie.poster_url = get_poster_for_movie(movie.title, movie.year)
            changed += 1
            continue

        if url in seen_urls:
            movie.poster_url = build_unique_placeholder(movie.title, movie.year, unique_suffix=movie.id)
            duplicate_fixes += 1
            changed += 1
        else:
            seen_urls[url] = movie.id

    if changed:
        db.session.commit()

    if duplicate_fixes:
        print(f"[posters] fixed duplicate poster URLs: {duplicate_fixes}")
    else:
        print("[posters] no duplicate poster URLs found")


def remove_duplicate_movies():
    """Remove duplicate movies by normalized title + year while preserving related data."""
    movies = Movie.query.order_by(Movie.id.asc()).all()
    groups = {}

    for movie in movies:
        key = ((movie.title or '').strip().lower(), movie.year)
        groups.setdefault(key, []).append(movie)

    removed_count = 0

    for duplicates in groups.values():
        if len(duplicates) <= 1:
            continue

        keeper = duplicates[0]
        duplicate_movies = duplicates[1:]

        for duplicate in duplicate_movies:
            duplicate_ratings = Rating.query.filter_by(movie_id=duplicate.id).all()
            for duplicate_rating in duplicate_ratings:
                keeper_rating = Rating.query.filter_by(
                    user_id=duplicate_rating.user_id,
                    movie_id=keeper.id
                ).first()

                if keeper_rating:
                    if duplicate_rating.rating > keeper_rating.rating:
                        keeper_rating.rating = duplicate_rating.rating
                    if not keeper_rating.review and duplicate_rating.review:
                        keeper_rating.review = duplicate_rating.review
                    db.session.delete(duplicate_rating)
                else:
                    duplicate_rating.movie_id = keeper.id

            duplicate_watchlist_items = Watchlist.query.filter_by(movie_id=duplicate.id).all()
            for duplicate_item in duplicate_watchlist_items:
                keeper_item = Watchlist.query.filter_by(
                    user_id=duplicate_item.user_id,
                    movie_id=keeper.id
                ).first()

                if keeper_item:
                    db.session.delete(duplicate_item)
                else:
                    duplicate_item.movie_id = keeper.id

            db.session.delete(duplicate)
            removed_count += 1

    if removed_count:
        db.session.commit()

    return removed_count


@app.cli.command('sync_posters')
def sync_posters_command():
    """Sync poster URLs and remove duplicate movies."""
    with app.app_context():
        ensure_movie_schema()
        streaming_result = import_streaming_catalog(
            region=os.environ.get('STREAMING_REGION', 'TH'),
            pages_per_provider=int(os.environ.get('STREAMING_MAX_PAGES', '5'))
        )
        if streaming_result.get('fallback_mode'):
            print(
                f"[streaming:fallback] providers={streaming_result.get('providers_found', 0)} "
                f"updated={streaming_result.get('updated', 0)}"
            )
        elif streaming_result.get('tmdb_enabled'):
            print(
                f"[streaming] providers={streaming_result.get('providers_found', 0)} "
                f"imported={streaming_result.get('imported', 0)} updated={streaming_result.get('updated', 0)}"
            )
        else:
            print('[streaming] TMDB_API_KEY not set; skipped provider import')
        removed = remove_duplicate_movies()
        sync_movie_posters()
        print(f"[movies] removed duplicate movies: {removed}")


@app.cli.command('import_streaming_catalog')
def import_streaming_catalog_command():
    """Import movie catalog from streaming providers via TMDB availability."""
    with app.app_context():
        ensure_movie_schema()
        result = import_streaming_catalog(
            region=os.environ.get('STREAMING_REGION', 'TH'),
            pages_per_provider=int(os.environ.get('STREAMING_MAX_PAGES', '8'))
        )

        if result.get('fallback_mode'):
            remove_duplicate_movies()
            sync_movie_posters()
            print(
                f"[streaming:fallback] providers={result.get('providers_found', 0)} "
                f"updated={result.get('updated', 0)}"
            )
            return

        remove_duplicate_movies()
        sync_movie_posters()
        print(
            f"[streaming] providers={result.get('providers_found', 0)} "
            f"imported={result.get('imported', 0)} updated={result.get('updated', 0)}"
        )


@app.before_request
def ensure_posters_ready_once():
    """Run one-time poster schema/sync update for existing databases"""
    requested_lang = request.args.get('lang')
    if requested_lang in SUPPORTED_LANGUAGES:
        session['lang'] = requested_lang

    if app.config.get('_posters_ready'):
        return

    ensure_movie_schema()
    seed_or_update_movie_catalog()
    remove_duplicate_movies()
    sync_movie_posters()
    app.config['_posters_ready'] = True


# ==================== Authentication Routes ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash(tf('flash.all_fields_required'), 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash(tf('flash.passwords_no_match'), 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash(tf('flash.username_exists'), 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash(tf('flash.email_exists'), 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash(tf('flash.register_success'), 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash(tf('flash.invalid_login'), 'danger')
            return redirect(url_for('login'))
        
        login_user(user)
        next_page = request.args.get('next')
        
        if not next_page or url_has_allowed_host_and_scheme(next_page):
            next_page = url_for('dashboard')
        
        flash(tf('flash.welcome_back', username=user.username), 'success')
        return redirect(next_page)
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash(tf('flash.logged_out'), 'info')
    return redirect(url_for('home'))


@app.route('/set-language/<lang_code>')
def set_language(lang_code):
    """Set UI language and return to previous page."""
    if lang_code in SUPPORTED_LANGUAGES:
        session['lang'] = lang_code

    referrer = request.referrer
    return redirect(referrer or url_for('home'))


def url_has_allowed_host_and_scheme(url, allowed_hosts=None):
    """Check if URL is safe to redirect to"""
    from urllib.parse import urlparse
    if allowed_hosts is None:
        allowed_hosts = {app.config['SERVER_NAME']} if app.config['SERVER_NAME'] else set()
    parsed = urlparse(url)
    return not parsed.netloc or parsed.netloc in allowed_hosts or parsed.netloc == 'localhost'


# ==================== Main Pages ====================

@app.route('/')
def home():
    """Home page with featured movies"""
    featured_movies = Movie.query.limit(6).all()
    return render_template('home.html', featured_movies=featured_movies)


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing ratings and watchlist stats"""
    user_ratings = Rating.query.filter_by(user_id=current_user.id).all()
    watchlist_count = Watchlist.query.filter_by(user_id=current_user.id).count()
    highly_rated = [r.movie for r in user_ratings if r.rating >= 4]
    
    return render_template('dashboard.html', 
                         user_ratings=user_ratings,
                         watchlist_count=watchlist_count,
                         highly_rated=highly_rated)


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user_ratings = Rating.query.filter_by(user_id=current_user.id).all()
    rating_count = len(user_ratings)
    avg_rating = round(sum(r.rating for r in user_ratings) / len(user_ratings), 2) if user_ratings else 0
    
    return render_template('profile.html', 
                         user_ratings=user_ratings,
                         rating_count=rating_count,
                         avg_rating=avg_rating)


# ==================== Movie Management Routes ====================

@app.route('/movies')
def movie_list():
    """Display all movies with optional filtering"""
    page = request.args.get('page', 1, type=int)
    genre = request.args.get('genre', None)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    min_rating = request.args.get('min_rating', type=float)
    sort_by = request.args.get('sort', 'newest')
    
    query = Movie.query
    
    if genre:
        query = query.filter_by(genre=genre)

    if year_from:
        query = query.filter(Movie.year >= year_from)

    if year_to:
        query = query.filter(Movie.year <= year_to)

    using_rating_aggregate = min_rating is not None and min_rating > 0

    if using_rating_aggregate:
        query = (
            query
            .outerjoin(Rating)
            .group_by(Movie.id)
            .having(func.coalesce(func.avg(Rating.rating), 0) >= min_rating)
        )

    if sort_by == 'oldest':
        query = query.order_by(Movie.year.asc(), Movie.title.asc())
    elif sort_by == 'title_asc':
        query = query.order_by(Movie.title.asc())
    elif sort_by == 'title_desc':
        query = query.order_by(Movie.title.desc())
    elif sort_by == 'rating_desc':
        if not using_rating_aggregate:
            query = query.outerjoin(Rating).group_by(Movie.id)
        query = query.order_by(func.coalesce(func.avg(Rating.rating), 0).desc(), Movie.title.asc())
    else:
        query = query.order_by(Movie.year.desc(), Movie.title.asc())
    
    movies = query.paginate(page=page, per_page=12)
    genres = db.session.query(Movie.genre).distinct().all()
    genres = [g[0] for g in genres]
    
    return render_template(
        'movie_list.html',
        movies=movies,
        genres=genres,
        selected_genre=genre,
        year_from=year_from,
        year_to=year_to,
        min_rating=min_rating,
        sort_by=sort_by
    )


@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """Display detailed information about a movie"""
    movie = Movie.query.get_or_404(movie_id)
    ratings = Rating.query.filter_by(movie_id=movie_id).all()
    user_rating = None
    in_watchlist = False
    
    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
        in_watchlist = Watchlist.query.filter_by(user_id=current_user.id, movie_id=movie_id).first() is not None
    
    return render_template('movie_detail.html', 
                         movie=movie,
                         ratings=ratings,
                         user_rating=user_rating,
                         in_watchlist=in_watchlist)


@app.route('/add-movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    """Add a new movie to the database"""
    if request.method == 'POST':
        title = request.form.get('title')
        genre = request.form.get('genre')
        year = request.form.get('year')
        description = request.form.get('description')
        
        # Validation
        if not all([title, genre, year, description]):
            flash(tf('flash.all_fields_required'), 'danger')
            return redirect(url_for('add_movie'))
        
        try:
            year = int(year)
            if year < 1800 or year > datetime.now().year + 1:
                flash(tf('flash.invalid_year'), 'danger')
                return redirect(url_for('add_movie'))
        except ValueError:
            flash(tf('flash.year_number'), 'danger')
            return redirect(url_for('add_movie'))
        
        # Check if movie already exists
        if Movie.query.filter_by(title=title, year=year).first():
            flash(tf('flash.movie_exists'), 'warning')
            return redirect(url_for('add_movie'))
        
        # Create movie
        movie = Movie(
            title=title,
            genre=genre,
            year=year,
            description=description,
            poster_url=get_poster_for_movie(title, year)
        )
        db.session.add(movie)
        db.session.commit()
        
        flash(tf('flash.movie_added', title=title), 'success')
        return redirect(url_for('movie_detail', movie_id=movie.id))
    
    return render_template('add_movie.html')


# ==================== Rating and Review Routes ====================

@app.route('/rate-movie/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def rate_movie(movie_id):
    """Rate and review a movie"""
    movie = Movie.query.get_or_404(movie_id)
    existing_rating = Rating.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        review = request.form.get('review', '').strip()
        
        # Validation
        if not rating or rating < 1 or rating > 5:
            flash(tf('flash.rating_range'), 'danger')
            return redirect(url_for('rate_movie', movie_id=movie_id))
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating
            existing_rating.review = review
            existing_rating.updated_at = datetime.utcnow()
            flash(tf('flash.rating_updated'), 'success')
        else:
            # Create new rating
            new_rating = Rating(user_id=current_user.id, movie_id=movie_id, 
                              rating=rating, review=review)
            db.session.add(new_rating)
            flash(tf('flash.rating_saved'), 'success')
        
        db.session.commit()
        return redirect(url_for('movie_detail', movie_id=movie_id))
    
    return render_template('rate_movie.html', movie=movie, existing_rating=existing_rating)


@app.route('/delete-rating/<int:rating_id>', methods=['POST'])
@login_required
def delete_rating(rating_id):
    """Delete a user's rating"""
    rating = Rating.query.get_or_404(rating_id)
    
    # Verify the rating belongs to the current user
    if rating.user_id != current_user.id:
        flash(tf('flash.no_permission'), 'danger')
        return redirect(url_for('home'))
    
    movie_id = rating.movie_id
    db.session.delete(rating)
    db.session.commit()
    
    flash(tf('flash.rating_deleted'), 'info')
    return redirect(url_for('movie_detail', movie_id=movie_id))


# ==================== Watchlist Routes ====================

@app.route('/watchlist')
@login_required
def watchlist():
    """Display user's watchlist"""
    page = request.args.get('page', 1, type=int)
    watchlist_items = Watchlist.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=12)
    
    return render_template('watchlist.html', watchlist=watchlist_items)


@app.route('/add-to-watchlist/<int:movie_id>', methods=['POST'])
@login_required
def add_to_watchlist(movie_id):
    """Add movie to watchlist"""
    movie = Movie.query.get_or_404(movie_id)
    
    # Check if already in watchlist
    if Watchlist.query.filter_by(user_id=current_user.id, movie_id=movie_id).first():
        return jsonify({'success': False, 'message': 'Already in watchlist'}), 400
    
    watchlist_item = Watchlist(user_id=current_user.id, movie_id=movie_id)
    db.session.add(watchlist_item)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'"{movie.title}" added to watchlist'})


@app.route('/remove-from-watchlist/<int:movie_id>', methods=['POST'])
@login_required
def remove_from_watchlist(movie_id):
    """Remove movie from watchlist"""
    movie = Movie.query.get_or_404(movie_id)
    watchlist_item = Watchlist.query.filter_by(user_id=current_user.id, movie_id=movie_id).first_or_404()
    
    db.session.delete(watchlist_item)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'"{movie.title}" removed from watchlist'})


# ==================== Recommendation Routes ====================

@app.route('/recommendations')
@login_required
def recommendations():
    """Generate movie recommendations based on user ratings"""
    # Get user's highly rated movies (4+ stars)
    user_ratings = Rating.query.filter_by(user_id=current_user.id).all()
    highly_rated_movies = [r.movie for r in user_ratings if r.rating >= 4]
    
    if not highly_rated_movies:
        flash(tf('flash.rate_for_recs'), 'info')
        return render_template('recommendations.html', recommendations=[], message=tf('msg.no_recs'))
    
    # Get genres from highly rated movies
    genres = set(movie.genre for movie in highly_rated_movies)
    
    # Find movies in the same genres that user hasn't rated
    rated_movie_ids = set(r.movie_id for r in user_ratings)
    
    recommended_movies = Movie.query.filter(
        Movie.genre.in_(list(genres)),
        ~Movie.id.in_(list(rated_movie_ids))
    ).limit(12).all()
    
    message = tf('msg.recs_based_on', genres=', '.join(genres)) if recommended_movies else tf('msg.no_recs')
    
    return render_template('recommendations.html', recommendations=recommended_movies, message=message)


# ==================== Search Routes ====================

@app.route('/search')
def search():
    """Search movies by title or genre"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    if not query or len(query) < 2:
        flash(tf('flash.search_min'), 'warning')
        return redirect(url_for('home'))
    
    # Search by title or genre
    search_results = Movie.query.filter(
        or_(
            Movie.title.ilike(f'%{query}%'),
            Movie.genre.ilike(f'%{query}%')
        )
    ).paginate(page=page, per_page=12)
    
    return render_template('search_results.html', 
                         results=search_results,
                         search_query=query)


@app.route('/search/suggest')
def search_suggest():
    """Return quick movie title suggestions for autocomplete"""
    query = request.args.get('q', '').strip()

    if len(query) < 2:
        return jsonify({'suggestions': []})

    suggestions = (
        Movie.query
        .filter(Movie.title.ilike(f'%{query}%'))
        .order_by(Movie.title.asc())
        .limit(8)
        .all()
    )

    return jsonify({
        'suggestions': [
            {'title': movie.title, 'year': movie.year}
            for movie in suggestions
        ]
    })


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('500.html'), 500


# ==================== Application Entry Point ====================

if __name__ == '__main__':
    # Initialize database and sample data
    init_db()
    
    # Run the application
    app.run(debug=True, host='127.0.0.1', port=5000)
