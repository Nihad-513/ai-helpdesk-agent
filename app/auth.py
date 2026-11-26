
"""Bean & Brew customer authentication interface."""

import streamlit as st
from database import register_customer, authenticate_customer


def show_auth():
    st.markdown(
        """
        <div class="brand-header">
            <div class="brand-icon">♨</div>
            <div class="brand-name">BEAN & BREW</div>
            <div class="brand-tagline">GOOD COFFEE. GREAT SUPPORT.</div>
        </div>
        <div class="auth-heading">
            <h1>Your coffee experience,<br>made better.</h1>
            <p>Sign in to manage orders, get support and track your requests.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 1.35, 1])

    with center:
        with st.container(border=True):
            tab_login, tab_register = st.tabs(
                ["Sign in", "Create account"]
            )

            with tab_login:
                st.markdown("### Welcome back")
                st.caption("Enter your details to access your account.")

                with st.form("login_form"):
                    email = st.text_input(
                        "Email address",
                        placeholder="you@example.com",
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
                        customer = authenticate_customer(email, password)

                        if customer:
                            st.session_state.staff_authenticated = False
                            st.session_state.staff = None

                            st.session_state.customer = customer
                            st.session_state.authenticated = True
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")

            with tab_register:
                st.markdown("### Join Bean & Brew")
                st.caption("Create an account to get started.")

                with st.form("register_form"):
                    name = st.text_input(
                        "Full name",
                        placeholder="Your name",
                    )
                    email = st.text_input(
                        "Email address",
                        placeholder="you@example.com",
                    )
                    password = st.text_input(
                        "Create password",
                        type="password",
                        placeholder="At least 8 characters",
                    )
                    confirm_password = st.text_input(
                        "Confirm password",
                        type="password",
                        placeholder="Re-enter your password",
                    )

                    submitted = st.form_submit_button(
                        "Create account →",
                        use_container_width=True,
                    )

                    if submitted:
                        if password != confirm_password:
                            st.error("Passwords do not match.")
                        else:
                            try:
                                register_customer(name, email, password)
                                st.success(
                                    "Account created! You can now sign in."
                                )
                            except ValueError as exc:
                                st.error(str(exc))

    st.markdown(
        """
        <div class="auth-footer">
            FRESHLY BREWED SUPPORT · BEAN & BREW
        </div>
        """,
        unsafe_allow_html=True,
    )
