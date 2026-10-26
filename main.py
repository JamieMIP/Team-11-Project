# main.py
from login_module import run_login
from gui_main import start_main_application

if __name__ == "__main__":
    # Launch login module
    user_id, login_time = run_login(show_theme_studio=False)

    # Use 'is not None' because user_id 0 (Admin) evaluates to False in a standard 'if user_id:' check
    if user_id is not None and login_time is not None:
        start_main_application(user_id, login_time)
    else:
        print("Login aborted or window closed.")