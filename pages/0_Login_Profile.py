import streamlit as st

from utils.auth_utils import (
    init_auth_state,
    is_logged_in,
    login,
    logout,
    register_profile,
    get_current_profile_name,
    change_password,
    delete_profile,
)
from utils.ui_utils import render_page_header


def main():
    init_auth_state()

    render_page_header(
        page_title="Login & Profile",
        subtitle="Secure your Period Buddy data behind a local profile on this device.",
    )

    if st.session_state.get("auth_locked"):
        st.error(
            "Too many failed login attempts in this session. "
            "Restart the app or wait a bit before trying again."
        )

    if not is_logged_in():
        tab_login, tab_register = st.tabs(["Login", "Register"])

        #  REGISTER
        with tab_register:
            st.markdown("#### Create a new profile")
            new_user = st.text_input("Username", key="reg_user")
            new_pass = st.text_input("Password / PIN", type="password", key="reg_pass")
            new_pass2 = st.text_input("Confirm password / PIN", type="password", key="reg_pass2")

            if st.button("Create profile"):
                if not new_user.strip() or not new_pass:
                    st.error("Username and password can’t be empty.")
                elif new_pass != new_pass2:
                    st.error("Passwords don’t match.")
                else:
                    ok = register_profile(new_user, new_pass)
                    if ok:
                        st.success("Profile created. You can log in from the Login tab.")
                    else:
                        st.error("Could not create profile. Username might already exist.")

        #  LOGIN
        with tab_login:
            st.markdown("#### Log in")
            user = st.text_input("Username", key="login_user")
            pw = st.text_input("Password / PIN", type="password", key="login_pw")

            if st.button("Login"):
                if st.session_state.get("auth_locked"):
                    st.error("Login is temporarily locked due to too many failed attempts.")
                else:
                    ok = login(user, pw)
                    if ok:
                        st.success("Logged in ✅")
                        st.rerun()
                    else:
                        st.error("Login failed. Wrong username/password or too many attempts.")
    else:
        current = get_current_profile_name() or "Unknown"
        st.success(f"Logged in as: {current}")

        col1, col2 = st.columns(2)

        #  LOGOUT
        with col1:
            st.markdown("#### Logout")
            if st.button("Logout"):
                logout()
                st.experimental_rerun()

        # CHANGE PW
        with col2:
            st.markdown("#### Change password")
            old_pw = st.text_input("Current password", type="password", key="cp_old")
            new_pw = st.text_input("New password", type="password", key="cp_new")
            new_pw2 = st.text_input("Confirm new password", type="password", key="cp_new2")

            if st.button("Update password"):
                if not old_pw or not new_pw:
                    st.error("Please fill all fields.")
                elif new_pw != new_pw2:
                    st.error("New passwords don’t match.")
                else:
                    ok = change_password(current, old_pw, new_pw)
                    if ok:
                        st.success("Password updated.")
                    else:
                        st.error("Could not change password. Check your current password.")

        st.markdown("---")
        st.markdown("#### Danger zone")

        st.caption(
            "Deleting your profile will permanently remove your local data for this user. "
            "This cannot be undone."
        )
        del_confirm = st.text_input(
            "Type DELETE to confirm profile deletion", key="del_confirm"
        )
        del_pw = st.text_input(
            "Password to confirm", type="password", key="del_pw"
        )

        if st.button("Delete my profile"):
            if del_confirm.strip().upper() != "DELETE":
                st.error("You must type DELETE to confirm.")
            elif not del_pw:
                st.error("Password is required to delete profile.")
            else:
                ok = delete_profile(current, del_pw)
                if ok:
                    st.success("Profile deleted.")
                    st.experimental_rerun()
                else:
                    st.error("Could not delete profile. Check your password.")


if __name__ == "__main__":
    main()
