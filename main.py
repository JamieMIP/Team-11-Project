# main.py
from login_module import run_login
from gui_main import start_main_application

if __name__ == "__main__":
    # Keep going back to the login screen until someone closes a window
    # instead of pressing Log Out.
    while True:
        # Launch login module
        user_id, login_time = run_login(show_theme_studio=False)

        # Use 'is not None' because user_id 0 (Admin) evaluates to False in a standard 'if user_id:' check
        if user_id is None or login_time is None:
            print("Login aborted or window closed.")
            break

        logged_out = start_main_application(user_id, login_time)
        if not logged_out:
            break
