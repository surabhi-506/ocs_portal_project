"""
Test database connection and verify data
Run this to ensure database is properly configured
"""

from database import get_db_connection, execute_query


def test_connection():
    """Test database connection and display users"""

    print("=" * 60)
    print("🔄 Testing Database Connection...")
    print("=" * 60)

    try:
        # Test basic connection
        connection = get_db_connection()
        print("✅ Database connected successfully!")
        connection.close()

        # Fetch all users
        print("\n📊 Fetching users from database...")
        users = execute_query("SELECT * FROM users ORDER BY role, userid", fetch_all=True)

        print(f"✅ Found {len(users)} users in database:")
        print("-" * 60)

        # Group by role for better display
        roles = {}
        for user in users:
            role = user['role']
            if role not in roles:
                roles[role] = []
            roles[role].append(user['userid'])

        # Display by role
        for role, userids in roles.items():
            print(f"\n{role.upper()}S:")
            for userid in userids:
                print(f"   • {userid}")

        # Test profiles
        print("\n" + "=" * 60)
        print("📋 Fetching job profiles...")
        profiles = execute_query("SELECT * FROM profile ORDER BY profile_code", fetch_all=True)

        print(f"✅ Found {len(profiles)} job profiles:")
        print("-" * 60)
        for profile in profiles:
            print(f"   [{profile['profile_code']}] {profile['company_name']} - {profile['designation']}")

        # Test applications
        print("\n" + "=" * 60)
        print("📝 Fetching applications...")
        applications = execute_query("SELECT * FROM application ORDER BY profile_code", fetch_all=True)

        print(f"✅ Found {len(applications)} applications:")
        print("-" * 60)
        for app in applications:
            print(f"   Profile {app['profile_code']} ← {app['entry_number']} ({app['status']})")

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED! Database is ready to use.")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("=" * 60)
        print("\n🔧 Troubleshooting:")
        print("1. Check if DATABASE_URL in .env is correct")
        print("2. Verify Supabase database is running")
        print("3. Ensure tables are created (users, profile, application)")
        print("4. Check if test data is inserted")
        print("=" * 60)
        return False


if __name__ == "__main__":
    test_connection()