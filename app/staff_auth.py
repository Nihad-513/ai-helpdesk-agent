
"""Bean & Brew staff authentication interface."""

import streamlit as st
from database import authenticate_staff


def show_staff_login():
    """Display the staff login page."""

    st.markdown(
        """
        <div class="brand-header">
            <div class="brand-icon">♨</div>
            <div class="brand-name">BEAN & BREW</div>
            <div class="brand-tagline">STAFF PORTAL</div>
        </div>
        <div class="auth-heading">
            <h1>Welcome back,<br>team.</h1>
            <p>Sign in to manage customer support and tickets.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 1.35, 1])

    with center:
        with st.container(border=True):
            st.markdown("### Staff sign in")
            st.caption("Access your support workspace.")

            with st.form("staff_login_form"):
                email = st.text_input(
                    "Work email",
                    placeholder="staff@beanbrew.com",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                )

                submitted = st.form_submit_button(
                    "Sign in →",
                    use_container_width=True,
                )

                if submitted:
                    staff = authenticate_staff(email, password)

                    if staff:
                      st.session_state.authenticated = False
                      st.session_state.customer = None

                      st.session_state.staff = staff
                      st.session_state.staff_authenticated = True
                      st.rerun()
                    else:
                        st.error("Invalid email or password.")

    st.markdown(
        """
        <div class="auth-footer">
            BEAN & BREW · INTERNAL SUPPORT PORTAL
        </div>
        """,
        unsafe_allow_html=True,
    )
