# 🔐 How to Login as Admin

## Quick Start

You need to:
1. **Register** a user account (if you don't have one)
2. **Promote** that user to admin
3. **Login** with that account
4. **Access** the admin panel

---

## Method 1: Via Web (Easiest)

### Step 1: Register Your Account
```
1. Go to: http://localhost:5000/auth/register
   (or your website URL)

2. Fill in the form:
   - Username: admin
   - Email: admin@example.com
   - Password: (must be 8+ characters, mix of letters/numbers/symbols)
   - Confirm Password: (same as above)

3. Click [Register]

4. You'll be redirected to Login page
```

### Step 2: Make Your Account Admin

Open a terminal in your project folder:

```powershell
# Windows PowerShell
.venv\Scripts\python.exe -c "
from app import create_app
from app.models import db, User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print('✅ User admin is now an administrator!')
    else:
        print('❌ User not found')
"
```

### Step 3: Login
```
1. Go to: http://localhost:5000/auth/login

2. Enter:
   - Username: admin
   - Password: (the password you set)

3. Click [Login]

4. ✓ You're logged in!
```

### Step 4: Access Admin Panel
```
1. Click your username in top menu

2. Click [Admin Panel]

3. Or go directly to:
   http://localhost:5000/admin/

4. ✓ Admin dashboard shows!
```

---

## Method 2: Via Python Script (Manual)

### Step 1: Create a script
Create a file called `make_admin.py`:

```python
from app import create_app
from app.models import db, User

app = create_app()

with app.app_context():
    # Option A: Make existing user admin
    user = User.query.filter_by(username='admin').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f'✅ {user.username} is now admin!')
    else:
        print('❌ User not found')
    
    # Option B: Create new admin user
    # new_user = User(
    #     username='admin',
    #     email='admin@example.com',
    #     is_admin=True
    # )
    # new_user.set_password('YourPassword123!')
    # db.session.add(new_user)
    # db.session.commit()
    # print(f'✅ Created admin user: {new_user.username}')
```

### Step 2: Run the script
```powershell
.venv\Scripts\python.exe make_admin.py
```

### Step 3: Login
Same as Method 1, Steps 3-4 above.

---

## Method 3: Direct Database (Advanced)

If you have database access:

```sql
-- SQLite
UPDATE users SET is_admin = 1 WHERE username = 'admin';

-- PostgreSQL
UPDATE users SET is_admin = true WHERE username = 'admin';
```

Then login normally.

---

## Method 4: Check If Already Admin

Run this to see all admin users:

```powershell
.venv\Scripts\python.exe -c "
from app import create_app
from app.models import User

app = create_app()
with app.app_context():
    admins = User.query.filter_by(is_admin=True).all()
    if admins:
        print('Current Admins:')
        for admin in admins:
            print(f'  • {admin.username} ({admin.email})')
    else:
        print('⚠️  No admins found yet')
"
```

---

## Step-by-Step Verification

### 1. Verify Registration Worked
```powershell
.venv\Scripts\python.exe -c "
from app import create_app
from app.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        print(f'✓ User found: {user.username}')
        print(f'  Email: {user.email}')
        print(f'  Admin: {user.is_admin}')
    else:
        print('✗ User not found')
"
```

### 2. Verify Admin Promotion Worked
```powershell
.venv\Scripts\python.exe -c "
from app import create_app
from app.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user and user.is_admin:
        print('✅ Admin status: Active!')
        print('   Ready to login and access admin panel')
    else:
        print('❌ Not admin yet')
"
```

### 3. Verify Login Works
```
1. Stop the server (if running)
2. Go to login page
3. Enter username and password
4. Should see: "Welcome [username]!"
```

### 4. Verify Admin Access
```
1. After logged in, look for "Admin Panel" in menu
2. Click it
3. Should see admin dashboard
4. Click "Manage Movies" to start editing
```

---

## Common Issues

### "I don't see Admin Panel in menu"
```
✗ Problem: Not logged in as admin
✓ Solution:
  1. Check if is_admin = true in database
  2. Re-run the admin promotion script
  3. Logout and login again
  4. Try incognito/private browser (clear cookies)
```

### "I ran make_admin.py but still no admin option"
```
✗ Problem: User not promoted yet
✓ Solution:
  1. Check user exists: python -c "..."
  2. Re-run make_admin.py
  3. Verify is_admin shows True
  4. Logout/login again
```

### "Can't remember password"
```
✓ Solution 1: Register a new admin account
✓ Solution 2: Reset password via email (if set up)
✓ Solution 3: Delete user from DB and create new one:
   
   .venv\Scripts\python.exe -c "
   from app import create_app
   from app.models import db, User
   
   app = create_app()
   with app.app_context():
       user = User.query.filter_by(username='admin').delete()
       db.session.commit()
       print('Old user deleted')
   "
   
   Then create new one via registration page
```

### "Admin button appears but access denied"
```
✗ Problem: The @admin_required decorator is blocking
✓ Solution:
  1. Check is_admin field in database
  2. Make sure it's True (not just 1)
  3. Logout completely and clear browser cookies
  4. Login fresh
  5. If still fails, check browser console for errors (F12)
```

---

## Success Checklist

After logging in as admin, you should see:

```
✅ Username in top right corner shows your username
✅ Menu has "Admin Panel" option (or dashboard link)
✅ Can click "Admin Panel" without error
✅ See dashboard with statistics
✅ Can click "Manage Movies" tab
✅ See list of all movies
✅ Each movie has [View] and [Edit] buttons
✅ Can click Edit and see form
```

If you see all these, you're fully set up as admin! 🎉

---

## Ready to Edit?

Once admin is set up:

```
1. Login as admin
2. Click Admin Panel
3. Click Manage Movies
4. Click [Edit] on any movie
5. Make your changes
6. Click [💾 Save Changes]
```

See **WHERE_TO_CLICK_EDIT_MOVIES.md** for visual navigation guide!

---

## Troubleshooting Commands

All-in-one verification:
```powershell
# Check user exists AND is admin
.venv\Scripts\python.exe -c "
from app import create_app
from app.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if not user:
        print('❌ User does not exist')
    elif not user.is_admin:
        print('⚠️  User exists but is NOT admin')
        print('   Run: .venv\\Scripts\\python.exe make_admin.py')
    else:
        print('✅ User is admin - ready to login!')
"
```

Then:
1. Go to login page
2. Enter username & password
3. Look for Admin Panel in menu
4. Click it - you're in!

**Questions?** Check the admin route is working:
```powershell
.venv\Scripts\python.exe -c "
from app import create_app

app = create_app()
routes = [str(r) for r in app.url_map.iter_rules() if '/admin' in str(r)]
print('Admin routes available:')
for r in sorted(routes):
    print(f'  {r}')
"
```

Should show routes like `/admin/movies`, `/admin/movies/<id>/edit`, etc.

Good luck! 🚀
