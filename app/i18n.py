"""
Minimal i18n utilities for the app templates.
"""

import json
from flask import session


SUPPORTED_LANGUAGES = {
    'en': 'English',
    'th': 'ไทย',
    'ja': '日本語',
    'zh': '中文',
    'es': 'Español',
}

TRANSLATIONS = {
    'nav.home': {'en': 'Home', 'th': 'หน้าแรก', 'ja': 'ホーム', 'zh': '首页', 'es': 'Inicio'},
    'nav.movies': {'en': 'Movies', 'th': 'ภาพยนตร์', 'ja': '映画', 'zh': '电影', 'es': 'Películas'},
    'nav.recommendations': {'en': 'Recommendations', 'th': 'แนะนำสำหรับคุณ', 'ja': 'おすすめ', 'zh': '推荐', 'es': 'Recomendaciones'},
    'nav.watchlist': {'en': 'Watchlist', 'th': 'รายการที่อยากดู', 'ja': 'ウォッチリスト', 'zh': '收藏清单', 'es': 'Lista'},
    'nav.dashboard': {'en': 'Dashboard', 'th': 'แดชบอร์ด', 'ja': 'ダッシュボード', 'zh': '仪表盘', 'es': 'Panel'},
    'nav.profile': {'en': 'Profile', 'th': 'โปรไฟล์', 'ja': 'プロフィール', 'zh': '个人资料', 'es': 'Perfil'},
    'nav.ratings': {'en': 'My Ratings', 'th': 'การให้คะแนนของฉัน', 'ja': '自分の評価', 'zh': '我的评分', 'es': 'Mis valoraciones'},
    'nav.settings': {'en': 'Settings', 'th': 'การตั้งค่า', 'ja': '設定', 'zh': '设置', 'es': 'Configuración'},
    'nav.admin': {'en': 'Admin Panel', 'th': 'แผงผู้ดูแล', 'ja': '管理パネル', 'zh': '管理面板', 'es': 'Panel admin'},
    'nav.logout': {'en': 'Logout', 'th': 'ออกจากระบบ', 'ja': 'ログアウト', 'zh': '退出登录', 'es': 'Cerrar sesión'},
    'nav.login': {'en': 'Login', 'th': 'เข้าสู่ระบบ', 'ja': 'ログイン', 'zh': '登录', 'es': 'Iniciar sesión'},
    'nav.register': {'en': 'Register', 'th': 'สมัครสมาชิก', 'ja': '登録', 'zh': '注册', 'es': 'Registrarse'},
    'nav.language': {'en': 'Language', 'th': 'ภาษา', 'ja': '言語', 'zh': '语言', 'es': 'Idioma'},
    'nav.theme': {'en': 'Toggle Theme', 'th': 'สลับธีม', 'ja': 'テーマ切替', 'zh': '切换主题', 'es': 'Cambiar tema'},
    'home.welcome': {'en': 'Welcome to FlickBase', 'th': 'ยินดีต้อนรับสู่ FlickBase', 'ja': 'FlickBaseへようこそ', 'zh': '欢迎来到 FlickBase', 'es': 'Bienvenido a FlickBase'},
    'home.tagline': {'en': 'Discover, rate, and share your favorite movies', 'th': 'ค้นพบ ให้คะแนน และแชร์ภาพยนตร์ที่คุณชื่นชอบ', 'ja': 'お気に入りの映画を見つけて評価し、共有しよう', 'zh': '发现、评分并分享你喜爱的电影', 'es': 'Descubre, califica y comparte tus películas favoritas'},
    'home.welcome_back': {'en': 'Welcome back,', 'th': 'ยินดีต้อนรับกลับ', 'ja': 'おかえりなさい、', 'zh': '欢迎回来，', 'es': 'Bienvenido de nuevo,'},
    'home.get_started': {'en': 'Get Started', 'th': 'เริ่มต้นใช้งาน', 'ja': 'はじめる', 'zh': '开始使用', 'es': 'Comenzar'},
    'home.get_recs': {'en': 'Get Recommendations', 'th': 'รับคำแนะนำ', 'ja': 'おすすめを見る', 'zh': '获取推荐', 'es': 'Ver recomendaciones'},
    'home.featured': {'en': 'Featured Movies', 'th': 'ภาพยนตร์แนะนำ', 'ja': '注目の映画', 'zh': '精选电影', 'es': 'Películas destacadas'},
    'home.trending': {'en': 'Trending Now', 'th': 'กำลังมาแรง', 'ja': '人気急上昇', 'zh': '正在流行', 'es': 'Tendencias'},
    'home.discover_more': {'en': 'Discover More', 'th': 'ค้นพบเพิ่มเติม', 'ja': 'さらに見る', 'zh': '发现更多', 'es': 'Descubrir más'},
    'home.discover_copy': {
        'en': 'Browse our entire collection of movies, rate them, and get personalized recommendations.',
        'th': 'สำรวจคลังภาพยนตร์ทั้งหมด ให้คะแนน และรับคำแนะนำเฉพาะคุณ',
        'ja': '映画コレクションを閲覧し、評価して、あなた向けのおすすめを受け取りましょう。',
        'zh': '浏览我们的全部电影收藏，评分并获取个性化推荐。',
        'es': 'Explora toda nuestra colección, califica películas y recibe recomendaciones personalizadas.'
    },
    'home.browse_all': {'en': 'Browse All Movies', 'th': 'ดูภาพยนตร์ทั้งหมด', 'ja': 'すべての映画を見る', 'zh': '浏览全部电影', 'es': 'Ver todas las películas'},
    'movies.collection': {'en': 'Movie Collection', 'th': 'คอลเลกชันภาพยนตร์', 'ja': '映画コレクション', 'zh': '电影收藏', 'es': 'Colección de películas'},
    'movies.filter_genre': {'en': 'Filter by Genre', 'th': 'กรองตามประเภท', 'ja': 'ジャンルで絞り込み', 'zh': '按类型筛选', 'es': 'Filtrar por género'},
    'movies.all_genres': {'en': 'All Genres', 'th': 'ทุกประเภท', 'ja': 'すべてのジャンル', 'zh': '全部类型', 'es': 'Todos los géneros'},
    'movies.sort_by': {'en': 'Sort by', 'th': 'เรียงตาม', 'ja': '並び替え', 'zh': '排序方式', 'es': 'Ordenar por'},
    'movies.sort_recent': {'en': 'Recent', 'th': 'ล่าสุด', 'ja': '新着', 'zh': '最新', 'es': 'Recientes'},
    'movies.sort_rating': {'en': 'Rating', 'th': 'คะแนน', 'ja': '評価', 'zh': '评分', 'es': 'Valoración'},
    'movies.sort_oldest': {'en': 'Oldest', 'th': 'เก่าสุด', 'ja': '古い順', 'zh': '最早', 'es': 'Más antiguas'},
    'movies.view_details': {'en': 'View Details', 'th': 'ดูรายละเอียด', 'ja': '詳細を見る', 'zh': '查看详情', 'es': 'Ver detalles'},
    'movies.none': {'en': 'No movies found. Try a different filter!', 'th': 'ไม่พบภาพยนตร์ ลองตัวกรองอื่น', 'ja': '映画が見つかりません。別の条件を試してください。', 'zh': '未找到电影，请尝试其他筛选条件。', 'es': 'No se encontraron películas. Prueba otro filtro.'},
    'search.title': {'en': 'Search Results for', 'th': 'ผลการค้นหาสำหรับ', 'ja': '検索結果', 'zh': '搜索结果', 'es': 'Resultados de búsqueda para'},
    'search.none': {'en': 'No movies found matching', 'th': 'ไม่พบภาพยนตร์ที่ตรงกับ', 'ja': '次に一致する映画は見つかりませんでした', 'zh': '未找到匹配的电影', 'es': 'No se encontraron películas que coincidan con'},
    'watchlist.title': {'en': 'My Watchlist', 'th': 'รายการที่อยากดูของฉัน', 'ja': 'マイウォッチリスト', 'zh': '我的收藏清单', 'es': 'Mi lista'},
    'watchlist.empty': {'en': 'Your watchlist is empty.', 'th': 'รายการที่อยากดูของคุณว่างอยู่', 'ja': 'ウォッチリストは空です。', 'zh': '你的收藏清单是空的。', 'es': 'Tu lista está vacía.'},
    'watchlist.browse': {'en': 'Browse movies', 'th': 'เรียกดูภาพยนตร์', 'ja': '映画を見る', 'zh': '浏览电影', 'es': 'Explorar películas'},
    'watchlist.remove': {'en': 'Remove', 'th': 'ลบออก', 'ja': '削除', 'zh': '移除', 'es': 'Eliminar'},
    'watchlist.view': {'en': 'View', 'th': 'ดู', 'ja': '見る', 'zh': '查看', 'es': 'Ver'},
    'detail.release_year': {'en': 'Release Year', 'th': 'ปีที่ฉาย', 'ja': '公開年', 'zh': '上映年份', 'es': 'Año de estreno'},
    'detail.genres': {'en': 'Genres', 'th': 'ประเภท', 'ja': 'ジャンル', 'zh': '类型', 'es': 'Géneros'},
    'detail.avg_rating': {'en': 'Average Rating', 'th': 'คะแนนเฉลี่ย', 'ja': '平均評価', 'zh': '平均评分', 'es': 'Valoración media'},
    'detail.description': {'en': 'Description', 'th': 'คำอธิบาย', 'ja': '説明', 'zh': '简介', 'es': 'Descripción'},
    'detail.add_watchlist': {'en': 'Add to Watchlist', 'th': 'เพิ่มในรายการที่อยากดู', 'ja': 'ウォッチリストに追加', 'zh': '加入收藏清单', 'es': 'Añadir a la lista'},
    'detail.remove_watchlist': {'en': 'Remove from Watchlist', 'th': 'ลบออกจากรายการที่อยากดู', 'ja': 'ウォッチリストから削除', 'zh': '从收藏清单移除', 'es': 'Quitar de la lista'},
    'detail.update_rating': {'en': 'Update Rating', 'th': 'อัปเดตคะแนน', 'ja': '評価を更新', 'zh': '更新评分', 'es': 'Actualizar valoración'},
    'detail.rate_movie': {'en': 'Rate This Movie', 'th': 'ให้คะแนนภาพยนตร์นี้', 'ja': 'この映画を評価', 'zh': '为这部电影评分', 'es': 'Valorar esta película'},
    'detail.login_rate': {'en': 'Login to Rate', 'th': 'เข้าสู่ระบบเพื่อให้คะแนน', 'ja': '評価するにはログイン', 'zh': '登录后评分', 'es': 'Inicia sesión para valorar'},
    'detail.your_rating': {'en': 'Your Rating', 'th': 'คะแนนของคุณ', 'ja': 'あなたの評価', 'zh': '你的评分', 'es': 'Tu valoración'},
    'detail.rated_on': {'en': 'Rated on', 'th': 'ให้คะแนนเมื่อ', 'ja': '評価日', 'zh': '评分于', 'es': 'Valorado el'},
    'detail.delete_rating': {'en': 'Delete Rating', 'th': 'ลบคะแนน', 'ja': '評価を削除', 'zh': '删除评分', 'es': 'Eliminar valoración'},
    'detail.ratings_reviews': {'en': 'Ratings & Reviews', 'th': 'คะแนนและรีวิว', 'ja': '評価とレビュー', 'zh': '评分与评论', 'es': 'Valoraciones y reseñas'},
    'detail.ratings_count': {'en': 'ratings', 'th': 'คะแนน', 'ja': '件の評価', 'zh': '条评分', 'es': 'valoraciones'},
    'detail.no_ratings': {'en': 'No ratings yet. Be the first to rate this movie!', 'th': 'ยังไม่มีคะแนน เป็นคนแรกที่ให้คะแนนภาพยนตร์นี้!', 'ja': 'まだ評価はありません。最初の評価を投稿しましょう！', 'zh': '还没有评分，来成为第一个评分的人吧！', 'es': 'Aún no hay valoraciones. ¡Sé la primera persona en puntuar esta película!'},
    'detail.confirm_delete': {'en': 'Are you sure you want to delete this rating?', 'th': 'คุณแน่ใจหรือไม่ว่าต้องการลบคะแนนนี้?', 'ja': 'この評価を削除してもよろしいですか？', 'zh': '确定要删除这条评分吗？', 'es': '¿Seguro que quieres eliminar esta valoración?'},
    'auth.login_heading': {'en': 'Login', 'th': 'เข้าสู่ระบบ', 'ja': 'ログイン', 'zh': '登录', 'es': 'Iniciar sesión'},
    'auth.register_heading': {'en': 'Register', 'th': 'สมัครสมาชิก', 'ja': '登録', 'zh': '注册', 'es': 'Registrarse'},
    'auth.username': {'en': 'Username', 'th': 'ชื่อผู้ใช้', 'ja': 'ユーザー名', 'zh': '用户名', 'es': 'Nombre de usuario'},
    'auth.email': {'en': 'Email', 'th': 'อีเมล', 'ja': 'メール', 'zh': '邮箱', 'es': 'Correo electrónico'},
    'auth.password': {'en': 'Password', 'th': 'รหัสผ่าน', 'ja': 'パスワード', 'zh': '密码', 'es': 'Contraseña'},
    'auth.confirm_password': {'en': 'Confirm Password', 'th': 'ยืนยันรหัสผ่าน', 'ja': 'パスワード確認', 'zh': '确认密码', 'es': 'Confirmar contraseña'},
    'auth.username_hint': {'en': '3-20 characters, letters/numbers/underscore only', 'th': '3-20 ตัวอักษร ใช้ได้เฉพาะตัวอักษร/ตัวเลข/ขีดล่าง', 'ja': '3〜20文字。英数字とアンダースコアのみ使用できます', 'zh': '3-20个字符，仅限字母/数字/下划线', 'es': '3-20 caracteres, solo letras/números/guion bajo'},
    'auth.password_hint': {'en': 'At least 6 characters', 'th': 'อย่างน้อย 6 ตัวอักษร', 'ja': '6文字以上', 'zh': '至少6个字符', 'es': 'Mínimo 6 caracteres'},
    'auth.no_account': {'en': "Don't have an account?", 'th': 'ยังไม่มีบัญชีใช่ไหม?', 'ja': 'アカウントをお持ちでないですか？', 'zh': '还没有账号？', 'es': '¿No tienes cuenta?'},
    'auth.have_account': {'en': 'Already have an account?', 'th': 'มีบัญชีอยู่แล้ว?', 'ja': 'すでにアカウントがありますか？', 'zh': '已有账号？', 'es': '¿Ya tienes cuenta?'},
    'auth.register_here': {'en': 'Register here', 'th': 'สมัครที่นี่', 'ja': 'こちらで登録', 'zh': '在此注册', 'es': 'Regístrate aquí'},
    'auth.login_here': {'en': 'Login here', 'th': 'เข้าสู่ระบบที่นี่', 'ja': 'こちらでログイン', 'zh': '在此登录', 'es': 'Inicia sesión aquí'},
    'recs.title': {'en': 'Recommendations', 'th': 'คำแนะนำ'},
    'recs.choose': {'en': 'Choose recommendation algorithm:', 'th': 'เลือกอัลกอริทึมแนะนำ:'},
    'recs.combined': {'en': 'Combined', 'th': 'ผสมผสาน'},
    'recs.genre': {'en': 'Genre-Based', 'th': 'ตามประเภท'},
    'recs.popular': {'en': 'Popular', 'th': 'ยอดนิยม'},
    'recs.collab': {'en': 'Collaborative', 'th': 'ร่วมมือ'},
    'recs.algo_genre': {'en': 'Genre-Based', 'th': 'ตามประเภท', 'ja': 'ジャンルベース', 'zh': '类型推荐', 'es': 'Por género'},
    'recs.algo_popular': {'en': 'Popular', 'th': 'ยอดนิยม', 'ja': '人気', 'zh': '热门', 'es': 'Populares'},
    'recs.algo_collab': {'en': 'Collaborative Filtering', 'th': 'คัดกรองร่วมกัน', 'ja': '協調フィルタリング', 'zh': '协同过滤', 'es': 'Filtrado colaborativo'},
    'recs.algo_combined': {'en': 'Personalized (Combined)', 'th': 'เฉพาะบุคคล (ผสม)', 'ja': 'パーソナライズ（複合）', 'zh': '个性化（综合）', 'es': 'Personalizado (combinado)'},
    'recs.none': {
        'en': 'No recommendations available. Rate more movies to get personalized recommendations!',
        'th': 'ยังไม่มีคำแนะนำ ให้คะแนนเพิ่มเติมเพื่อรับคำแนะนำที่ตรงใจ'
    },
    'recs.start_rating': {'en': 'Start rating movies', 'th': 'เริ่มให้คะแนนภาพยนตร์'},
    'pagination.previous': {'en': 'Previous', 'th': 'ก่อนหน้า'},
    'pagination.next': {'en': 'Next', 'th': 'ถัดไป'},
    'common.view': {'en': 'View', 'th': 'ดู'},
    'common.remove': {'en': 'Remove', 'th': 'ลบออก'},
    'footer.description': {
        'en': 'Discover, rate, and share your favorite movies with our community.',
        'th': 'ค้นพบ ให้คะแนน และแชร์หนังเรื่องโปรดของคุณกับชุมชนของเรา',
        'ja': 'お気に入りの映画を見つけ、評価し、コミュニティと共有しましょう。',
        'zh': '与我们的社区一起发现、评分并分享你喜爱的电影。',
        'es': 'Descubre, califica y comparte tus películas favoritas con nuestra comunidad.'
    },
    'footer.quick_links': {'en': 'Quick Links', 'th': 'ลิงก์ด่วน', 'ja': 'クイックリンク', 'zh': '快速链接', 'es': 'Enlaces rápidos'},
    'footer.follow_us': {'en': 'Follow Us', 'th': 'ติดตามเรา', 'ja': 'フォローする', 'zh': '关注我们', 'es': 'Síguenos'},
    'footer.rights': {'en': 'All rights reserved.', 'th': 'สงวนลิขสิทธิ์', 'ja': '無断転載を禁じます。', 'zh': '版权所有。', 'es': 'Todos los derechos reservados.'},
    'flash.register_success': {'en': 'Registration successful! Please log in.', 'th': 'สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ', 'ja': '登録が完了しました。ログインしてください。', 'zh': '注册成功！请登录。', 'es': '¡Registro exitoso! Inicia sesión.'},
    'flash.register_error': {'en': 'An error occurred during registration. Please try again.', 'th': 'เกิดข้อผิดพลาดระหว่างสมัครสมาชิก โปรดลองอีกครั้ง', 'ja': '登録中にエラーが発生しました。もう一度お試しください。', 'zh': '注册时发生错误，请重试。', 'es': 'Ocurrió un error durante el registro. Inténtalo de nuevo.'},
    'flash.invalid_login': {'en': 'Invalid username or password.', 'th': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'ja': 'ユーザー名またはパスワードが正しくありません。', 'zh': '用户名或密码错误。', 'es': 'Usuario o contraseña inválidos.'},
    'flash.welcome_back': {'en': 'Welcome back, {username}!', 'th': 'ยินดีต้อนรับกลับ, {username}!', 'ja': 'おかえりなさい、{username}さん！', 'zh': '欢迎回来，{username}！', 'es': '¡Bienvenido de nuevo, {username}!'},
    'flash.logged_out': {'en': 'You have been logged out.', 'th': 'คุณได้ออกจากระบบแล้ว', 'ja': 'ログアウトしました。', 'zh': '你已退出登录。', 'es': 'Has cerrado sesión.'},
    'flash.movie_exists': {'en': 'This movie already exists in the database.', 'th': 'ภาพยนตร์นี้มีอยู่แล้วในฐานข้อมูล', 'ja': 'この映画はすでにデータベースに存在します。', 'zh': '该电影已存在于数据库中。', 'es': 'Esta película ya existe en la base de datos.'},
    'flash.movie_added': {'en': 'Movie "{title}" added successfully!', 'th': 'เพิ่มภาพยนตร์ "{title}" สำเร็จ!', 'ja': '映画「{title}」を追加しました！', 'zh': '电影“{title}”添加成功！', 'es': '¡Película "{title}" añadida correctamente!'},
    'flash.movie_add_error': {'en': 'An error occurred while adding the movie.', 'th': 'เกิดข้อผิดพลาดขณะเพิ่มภาพยนตร์', 'ja': '映画の追加中にエラーが発生しました。', 'zh': '添加电影时发生错误。', 'es': 'Ocurrió un error al añadir la película.'},
    'flash.rating_updated': {'en': 'Your rating has been updated.', 'th': 'อัปเดตคะแนนของคุณแล้ว', 'ja': '評価を更新しました。', 'zh': '你的评分已更新。', 'es': 'Tu valoración se ha actualizado.'},
    'flash.rating_saved': {'en': 'Your rating has been saved.', 'th': 'บันทึกคะแนนของคุณแล้ว', 'ja': '評価を保存しました。', 'zh': '你的评分已保存。', 'es': 'Tu valoración se ha guardado.'},
    'flash.rating_save_error': {'en': 'An error occurred while saving your rating.', 'th': 'เกิดข้อผิดพลาดขณะบันทึกคะแนนของคุณ', 'ja': '評価の保存中にエラーが発生しました。', 'zh': '保存评分时发生错误。', 'es': 'Ocurrió un error al guardar tu valoración.'},
    'flash.search_min': {'en': 'Please enter at least 2 characters to search.', 'th': 'กรุณากรอกอย่างน้อย 2 ตัวอักษรเพื่อค้นหา', 'ja': '検索するには2文字以上入力してください。', 'zh': '搜索请至少输入2个字符。', 'es': 'Introduce al menos 2 caracteres para buscar.'},
    'flash.recs_prompt': {'en': 'Rate some movies to get personalized recommendations!', 'th': 'ให้คะแนนภาพยนตร์เพื่อรับคำแนะนำเฉพาะคุณ!', 'ja': '映画を評価してパーソナライズおすすめを受け取りましょう！', 'zh': '先评分一些电影以获取个性化推荐！', 'es': '¡Valora algunas películas para obtener recomendaciones personalizadas!'},
    'api.unauthorized': {'en': 'Unauthorized', 'th': 'ไม่ได้รับอนุญาต', 'ja': '権限がありません', 'zh': '未授权', 'es': 'No autorizado'},
    'api.rating_deleted': {'en': 'Rating deleted successfully', 'th': 'ลบคะแนนสำเร็จ', 'ja': '評価を削除しました', 'zh': '评分已删除', 'es': 'Valoración eliminada correctamente'},
    'api.rating_delete_error': {'en': 'Error deleting rating', 'th': 'เกิดข้อผิดพลาดในการลบคะแนน', 'ja': '評価の削除中にエラーが発生しました', 'zh': '删除评分时出错', 'es': 'Error al eliminar la valoración'},
    'api.watchlist_exists': {'en': 'Movie already in watchlist', 'th': 'ภาพยนตร์นี้อยู่ในรายการที่อยากดูแล้ว', 'ja': 'この映画はすでにウォッチリストにあります', 'zh': '该电影已在收藏清单中', 'es': 'La película ya está en la lista'},
    'api.watchlist_added': {'en': '"{title}" added to watchlist', 'th': 'เพิ่ม "{title}" ลงในรายการที่อยากดูแล้ว', 'ja': '「{title}」をウォッチリストに追加しました', 'zh': '“{title}”已加入收藏清单', 'es': '"{title}" se añadió a la lista'},
    'api.watchlist_add_error': {'en': 'Error adding to watchlist', 'th': 'เกิดข้อผิดพลาดในการเพิ่มรายการที่อยากดู', 'ja': 'ウォッチリストへの追加中にエラーが発生しました', 'zh': '加入收藏清单时出错', 'es': 'Error al añadir a la lista'},
    'api.watchlist_removed': {'en': '"{title}" removed from watchlist', 'th': 'ลบ "{title}" ออกจากรายการที่อยากดูแล้ว', 'ja': '「{title}」をウォッチリストから削除しました', 'zh': '“{title}”已从收藏清单移除', 'es': '"{title}" se eliminó de la lista'},
    'api.watchlist_remove_error': {'en': 'Error removing from watchlist', 'th': 'เกิดข้อผิดพลาดในการลบจากรายการที่อยากดู', 'ja': 'ウォッチリストからの削除中にエラーが発生しました', 'zh': '从收藏清单移除时出错', 'es': 'Error al quitar de la lista'},
    'flash.email_invalid': {'en': 'Please provide a valid email address.', 'th': 'กรุณากรอกอีเมลที่ถูกต้อง', 'ja': '有効なメールアドレスを入力してください。', 'zh': '请输入有效的邮箱地址。', 'es': 'Introduce un correo válido.'},
    'flash.email_in_use': {'en': 'Email already in use.', 'th': 'อีเมลนี้ถูกใช้งานแล้ว', 'ja': 'このメールアドレスはすでに使用されています。', 'zh': '该邮箱已被使用。', 'es': 'El correo ya está en uso.'},
    'flash.email_updated': {'en': 'Email updated successfully!', 'th': 'อัปเดตอีเมลสำเร็จ!', 'ja': 'メールアドレスを更新しました！', 'zh': '邮箱更新成功！', 'es': '¡Correo actualizado correctamente!'},
    'flash.email_update_error': {'en': 'Error updating email.', 'th': 'เกิดข้อผิดพลาดในการอัปเดตอีเมล', 'ja': 'メールアドレス更新中にエラーが発生しました。', 'zh': '更新邮箱时出错。', 'es': 'Error al actualizar el correo.'},
    'flash.password_current_invalid': {'en': 'Current password is incorrect.', 'th': 'รหัสผ่านปัจจุบันไม่ถูกต้อง', 'ja': '現在のパスワードが正しくありません。', 'zh': '当前密码不正确。', 'es': 'La contraseña actual es incorrecta.'},
    'flash.password_mismatch': {'en': 'New passwords do not match.', 'th': 'รหัสผ่านใหม่ไม่ตรงกัน', 'ja': '新しいパスワードが一致しません。', 'zh': '新密码不一致。', 'es': 'Las nuevas contraseñas no coinciden.'},
    'flash.password_min_length': {'en': 'Password must be at least 6 characters long.', 'th': 'รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร', 'ja': 'パスワードは6文字以上で入力してください。', 'zh': '密码至少需要6个字符。', 'es': 'La contraseña debe tener al menos 6 caracteres.'},
    'flash.password_updated': {'en': 'Password updated successfully!', 'th': 'อัปเดตรหัสผ่านสำเร็จ!', 'ja': 'パスワードを更新しました！', 'zh': '密码更新成功！', 'es': '¡Contraseña actualizada correctamente!'},
    'flash.password_update_error': {'en': 'Error updating password.', 'th': 'เกิดข้อผิดพลาดในการอัปเดตรหัสผ่าน', 'ja': 'パスワード更新中にエラーが発生しました。', 'zh': '更新密码时出错。', 'es': 'Error al actualizar la contraseña.'},
    'rate.heading': {'en': 'Rate: {title}', 'th': 'ให้คะแนน: {title}', 'ja': '評価: {title}', 'zh': '评分: {title}', 'es': 'Valorar: {title}'},
    'rate.current': {'en': 'Current Rating:', 'th': 'คะแนนปัจจุบัน:', 'ja': '現在の評価:', 'zh': '当前评分：', 'es': 'Valoración actual:'},
    'rate.not_rated': {'en': 'Not rated yet', 'th': 'ยังไม่ได้ให้คะแนน', 'ja': 'まだ評価していません', 'zh': '尚未评分', 'es': 'Sin valorar aún'},
    'rate.select_placeholder': {'en': '-- Select a rating --', 'th': '-- เลือกคะแนน --', 'ja': '-- 評価を選択 --', 'zh': '-- 选择评分 --', 'es': '-- Selecciona una valoración --'},
    'rate.excellent': {'en': 'Excellent', 'th': 'ยอดเยี่ยม', 'ja': '最高', 'zh': '优秀', 'es': 'Excelente'},
    'rate.very_good': {'en': 'Very Good', 'th': 'ดีมาก', 'ja': 'とても良い', 'zh': '很好', 'es': 'Muy buena'},
    'rate.good': {'en': 'Good', 'th': 'ดี', 'ja': '良い', 'zh': '不错', 'es': 'Buena'},
    'rate.fair': {'en': 'Fair', 'th': 'พอใช้', 'ja': '普通', 'zh': '一般', 'es': 'Regular'},
    'rate.poor': {'en': 'Poor', 'th': 'แย่', 'ja': '悪い', 'zh': '较差', 'es': 'Mala'},
    'rate.review_placeholder': {'en': 'Share your thoughts about this movie...', 'th': 'แบ่งปันความเห็นของคุณเกี่ยวกับภาพยนตร์เรื่องนี้...', 'ja': 'この映画について感想を書いてください...', 'zh': '分享你对这部电影的看法...', 'es': 'Comparte tu opinión sobre esta película...'},
    'rate.review_hint': {'en': 'Optional - Max 1000 characters', 'th': 'ไม่บังคับ - สูงสุด 1000 ตัวอักษร', 'ja': '任意 - 最大1000文字', 'zh': '可选 - 最多1000字符', 'es': 'Opcional - Máximo 1000 caracteres'},
    'rate.save': {'en': 'Save Rating', 'th': 'บันทึกคะแนน', 'ja': '評価を保存', 'zh': '保存评分', 'es': 'Guardar valoración'},
    'rate.back_to_movie': {'en': 'Back to Movie', 'th': 'กลับไปหน้าภาพยนตร์', 'ja': '映画ページへ戻る', 'zh': '返回电影页', 'es': 'Volver a la película'},
    'watchlist.confirm_remove': {'en': 'Remove from watchlist?', 'th': 'ลบออกจากรายการที่อยากดูหรือไม่?', 'ja': 'ウォッチリストから削除しますか？', 'zh': '要从收藏清单中移除吗？', 'es': '¿Quitar de la lista?'},
    'settings.title': {'en': 'Account Settings', 'th': 'การตั้งค่าบัญชี', 'ja': 'アカウント設定', 'zh': '账户设置', 'es': 'Configuración de la cuenta'},
    'settings.change_email': {'en': 'Change Email', 'th': 'เปลี่ยนอีเมล', 'ja': 'メールを変更', 'zh': '更改邮箱', 'es': 'Cambiar correo'},
    'settings.current_email': {'en': 'Current Email', 'th': 'อีเมลปัจจุบัน', 'ja': '現在のメール', 'zh': '当前邮箱', 'es': 'Correo actual'},
    'settings.new_email': {'en': 'New Email', 'th': 'อีเมลใหม่', 'ja': '新しいメール', 'zh': '新邮箱', 'es': 'Nuevo correo'},
    'settings.update_email': {'en': 'Update Email', 'th': 'อัปเดตอีเมล', 'ja': 'メールを更新', 'zh': '更新邮箱', 'es': 'Actualizar correo'},
    'settings.change_password': {'en': 'Change Password', 'th': 'เปลี่ยนรหัสผ่าน', 'ja': 'パスワードを変更', 'zh': '更改密码', 'es': 'Cambiar contraseña'},
    'settings.current_password': {'en': 'Current Password', 'th': 'รหัสผ่านปัจจุบัน', 'ja': '現在のパスワード', 'zh': '当前密码', 'es': 'Contraseña actual'},
    'settings.new_password': {'en': 'New Password', 'th': 'รหัสผ่านใหม่', 'ja': '新しいパスワード', 'zh': '新密码', 'es': 'Nueva contraseña'},
    'settings.confirm_new_password': {'en': 'Confirm New Password', 'th': 'ยืนยันรหัสผ่านใหม่', 'ja': '新しいパスワードを確認', 'zh': '确认新密码', 'es': 'Confirmar nueva contraseña'},
    'settings.update_password': {'en': 'Update Password', 'th': 'อัปเดตรหัสผ่าน', 'ja': 'パスワードを更新', 'zh': '更新密码', 'es': 'Actualizar contraseña'},
    'settings.password_hint': {'en': 'At least 6 characters', 'th': 'อย่างน้อย 6 ตัวอักษร', 'ja': '6文字以上', 'zh': '至少6个字符', 'es': 'Mínimo 6 caracteres'},
    'settings.danger_zone': {'en': 'Danger Zone', 'th': 'โซนอันตราย', 'ja': '危険ゾーン', 'zh': '危险区域', 'es': 'Zona de riesgo'},
    'settings.delete_warning': {'en': 'Deleting your account is permanent and cannot be undone.', 'th': 'การลบบัญชีเป็นการถาวรและไม่สามารถย้อนกลับได้', 'ja': 'アカウント削除は取り消せない恒久的な操作です。', 'zh': '删除账户是永久操作且无法撤销。', 'es': 'Eliminar tu cuenta es permanente y no se puede deshacer.'},
    'settings.delete_account': {'en': 'Delete Account', 'th': 'ลบบัญชี', 'ja': 'アカウントを削除', 'zh': '删除账户', 'es': 'Eliminar cuenta'},
    'settings.delete_modal_title': {'en': 'Delete Account', 'th': 'ลบบัญชี', 'ja': 'アカウント削除', 'zh': '删除账户', 'es': 'Eliminar cuenta'},
    'settings.warning': {'en': 'Warning:', 'th': 'คำเตือน:', 'ja': '警告:', 'zh': '警告：', 'es': 'Advertencia:'},
    'settings.delete_modal_text': {'en': 'This action is permanent and cannot be undone!', 'th': 'การกระทำนี้ถาวรและไม่สามารถย้อนกลับได้!', 'ja': 'この操作は取り消せません！', 'zh': '此操作不可撤销！', 'es': '¡Esta acción es permanente y no se puede deshacer!'},
    'settings.delete_data_text': {'en': 'All your ratings, watchlist, and account data will be deleted.', 'th': 'คะแนน รายการที่อยากดู และข้อมูลบัญชีทั้งหมดจะถูกลบ', 'ja': '評価、ウォッチリスト、アカウント情報がすべて削除されます。', 'zh': '你的评分、收藏清单和账户数据都将被删除。', 'es': 'Se eliminarán todas tus valoraciones, lista y datos de cuenta.'},
    'settings.type_username': {'en': 'Type your username to confirm:', 'th': 'พิมพ์ชื่อผู้ใช้เพื่อยืนยัน:', 'ja': '確認のためユーザー名を入力してください:', 'zh': '输入用户名以确认：', 'es': 'Escribe tu usuario para confirmar:'},
    'common.cancel': {'en': 'Cancel', 'th': 'ยกเลิก', 'ja': 'キャンセル', 'zh': '取消', 'es': 'Cancelar'},
    'settings.delete_my_account': {'en': 'Delete My Account', 'th': 'ลบบัญชีของฉัน', 'ja': '自分のアカウントを削除', 'zh': '删除我的账户', 'es': 'Eliminar mi cuenta'},
    'settings.confirm_final': {'en': 'This cannot be undone. Are you absolutely sure?', 'th': 'ไม่สามารถย้อนกลับได้ คุณแน่ใจใช่ไหม?', 'ja': '取り消せません。本当に実行しますか？', 'zh': '此操作无法撤销，确定继续吗？', 'es': 'No se puede deshacer. ¿Estás seguro?'},
    'settings.delete_not_implemented': {'en': 'Account deletion not yet implemented', 'th': 'ยังไม่ได้พัฒนาการลบบัญชี', 'ja': 'アカウント削除は未実装です', 'zh': '账户删除功能尚未实现', 'es': 'La eliminación de cuenta aún no está implementada'},
    'settings.username_mismatch': {'en': 'Username does not match', 'th': 'ชื่อผู้ใช้ไม่ตรงกัน', 'ja': 'ユーザー名が一致しません', 'zh': '用户名不匹配', 'es': 'El nombre de usuario no coincide'},
    'admin.no_permission': {'en': 'You do not have permission to access this page.', 'th': 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'ja': 'このページにアクセスする権限がありません。', 'zh': '你没有权限访问此页面。', 'es': 'No tienes permiso para acceder a esta página.'},
    'admin.cannot_modify_self': {'en': 'Cannot modify your own admin status.', 'th': 'ไม่สามารถเปลี่ยนสถานะแอดมินของตัวเองได้', 'ja': '自分の管理者ステータスは変更できません。', 'zh': '不能修改自己的管理员状态。', 'es': 'No puedes modificar tu propio estado de administrador.'},
    'admin.user_updated_error': {'en': 'Error updating user.', 'th': 'เกิดข้อผิดพลาดในการอัปเดตผู้ใช้', 'ja': 'ユーザー更新中にエラーが発生しました。', 'zh': '更新用户时出错。', 'es': 'Error al actualizar el usuario.'},
    'admin.cannot_delete_self': {'en': 'Cannot delete your own account.', 'th': 'ไม่สามารถลบบัญชีตัวเองได้', 'ja': '自分のアカウントは削除できません。', 'zh': '不能删除自己的账户。', 'es': 'No puedes eliminar tu propia cuenta.'},
    'admin.user_deleted': {'en': 'User "{username}" has been deleted.', 'th': 'ลบผู้ใช้ "{username}" แล้ว', 'ja': 'ユーザー「{username}」を削除しました。', 'zh': '用户“{username}”已删除。', 'es': 'El usuario "{username}" ha sido eliminado.'},
    'admin.user_delete_error': {'en': 'Error deleting user.', 'th': 'เกิดข้อผิดพลาดในการลบผู้ใช้', 'ja': 'ユーザー削除中にエラーが発生しました。', 'zh': '删除用户时出错。', 'es': 'Error al eliminar el usuario.'},
    'admin.movie_deleted': {'en': 'Movie "{title}" has been deleted.', 'th': 'ลบภาพยนตร์ "{title}" แล้ว', 'ja': '映画「{title}」を削除しました。', 'zh': '电影“{title}”已删除。', 'es': 'La película "{title}" ha sido eliminada.'},
    'admin.movie_delete_error': {'en': 'Error deleting movie.', 'th': 'เกิดข้อผิดพลาดในการลบภาพยนตร์', 'ja': '映画削除中にエラーが発生しました。', 'zh': '删除电影时出错。', 'es': 'Error al eliminar la película.'},
    'admin.rating_deleted': {'en': 'Rating deleted successfully.', 'th': 'ลบคะแนนเรียบร้อยแล้ว', 'ja': '評価を削除しました。', 'zh': '评分已成功删除。', 'es': 'Valoración eliminada correctamente.'},
    'admin.rating_delete_error': {'en': 'Error deleting rating.', 'th': 'เกิดข้อผิดพลาดในการลบคะแนน', 'ja': '評価削除中にエラーが発生しました。', 'zh': '删除评分时出错。', 'es': 'Error al eliminar la valoración.'},
    'admin.genre_name_required': {'en': 'Genre name is required.', 'th': 'จำเป็นต้องระบุชื่อประเภท', 'ja': 'ジャンル名は必須です。', 'zh': '必须填写类型名称。', 'es': 'El nombre del género es obligatorio.'},
    'admin.genre_exists': {'en': 'Genre already exists.', 'th': 'ประเภทนี้มีอยู่แล้ว', 'ja': 'そのジャンルは既に存在します。', 'zh': '该类型已存在。', 'es': 'El género ya existe.'},
    'admin.genre_added': {'en': 'Genre "{name}" added successfully.', 'th': 'เพิ่มประเภท "{name}" สำเร็จ', 'ja': 'ジャンル「{name}」を追加しました。', 'zh': '类型“{name}”添加成功。', 'es': 'Género "{name}" añadido correctamente.'},
    'admin.genre_add_error': {'en': 'Error adding genre.', 'th': 'เกิดข้อผิดพลาดในการเพิ่มประเภท', 'ja': 'ジャンル追加中にエラーが発生しました。', 'zh': '添加类型时出错。', 'es': 'Error al añadir el género.'},
    'admin.genre_deleted': {'en': 'Genre "{name}" deleted successfully.', 'th': 'ลบประเภท "{name}" สำเร็จ', 'ja': 'ジャンル「{name}」を削除しました。', 'zh': '类型“{name}”删除成功。', 'es': 'Género "{name}" eliminado correctamente.'},
    'admin.genre_delete_error': {'en': 'Error deleting genre.', 'th': 'เกิดข้อผิดพลาดในการลบประเภท', 'ja': 'ジャンル削除中にエラーが発生しました。', 'zh': '删除类型时出错。', 'es': 'Error al eliminar el género.'},
}


def get_current_language():
    """Return the active language code."""
    selected = session.get('lang')
    return selected if selected in SUPPORTED_LANGUAGES else 'en'


def translate(key, lang=None):
    """Translate a key to the current language, fallback to English."""
    current_lang = lang or get_current_language()
    entry = TRANSLATIONS.get(key, {})
    return entry.get(current_lang) or entry.get('en') or key


def localize_text(value, lang=None):
    """Return localized text from a JSON object stored as a string."""
    if value is None:
        return ''
    if not isinstance(value, str):
        return value
    try:
        payload = json.loads(value)
    except Exception:
        return value
    if isinstance(payload, dict):
        current_lang = lang or get_current_language()
        return payload.get(current_lang) or payload.get('en') or next(iter(payload.values()), value)
    return value
