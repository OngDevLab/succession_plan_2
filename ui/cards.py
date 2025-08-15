"""
Card display components for incumbents and successors
"""

import streamlit as st

def display_selected_incumbent_card(incumbent, show_button=True):
    person = incumbent['metadata']
    plan = incumbent['plan_details']
    full_name = f"{person['PREFERRED_NAME_FIRST_NAME']} {person['PREFERRED_NAME_LAST_NAME']}"

    if show_button:
        st.subheader("Selected Incumbent")

    with st.container(border=True):
        c1, c2 = st.columns([1, 5])
        with c1:
            st.image(f"https://rostr.disney.com/api/v2/people/{person['EMPLOYEE_ID']}/avatars/thumbnail_large?locale=en&token=abc4fc58f30914f6d99faa8a31f4d44c", width=100)
        with c2:
            st.markdown(f"### {full_name}")
            st.markdown(f"**Position:** {person['POSITION_NBR_DESCRIPTION']}")
            critical_text = "Yes" if plan.get('critical_role') else "No"
            st.markdown(f"**Critical Role?** `{critical_text}` | **Sourcing Strategy:** `{plan.get('sourcing_strategy', 'N/A')}`")
            st.markdown(f"**Scenario:** `{plan.get('scenario_plan', 'N/A')}`")

            with st.expander("View Additional Plan Details"):
                # 1. Critical Role
                st.markdown(f"**Critical Role:** {critical_text}")
                
                # 2. Contract End Date (Optional)
                if plan.get('contract_end_date'):
                    st.markdown(f"**Contract End Date:** {plan.get('contract_end_date')}")
                else:
                    st.markdown(f"**Contract End Date:** Not specified")
                
                # 4. Top Demonstrated People Leader Expectation
                st.markdown(f"**Top Demonstrated People Leader Expectation:**")
                st.info(plan.get('top_ple', 'Not specified.'))
                
                # 5. Top Leadership Skills
                st.markdown(f"**Top Leadership Skills:**")
                st.info(", ".join(plan.get('top_skills', ['Not specified.'])))
                
                # 6. Talent Sourcing Strategy
                sourcing_display = plan.get('sourcing_strategy', [])
                if isinstance(sourcing_display, list):
                    sourcing_text = ", ".join(sourcing_display) if sourcing_display else 'Not specified'
                else:
                    sourcing_text = sourcing_display if sourcing_display else 'Not specified'
                st.markdown(f"**Talent Sourcing Strategy:** {sourcing_text}")
                
                # 7. Scenario Plan
                st.markdown(f"**Scenario Plan:** {plan.get('scenario_plan', 'Not specified')}")
                
                # 8. Type of Role (optional)
                if plan.get('role_type') and plan.get('role_type') != 'Not Applicable':
                    st.markdown(f"**Type of Role:** {plan.get('role_type')}")

    if show_button:
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            if st.button("🔄 Start Over", use_container_width=True, help="Start a new succession plan from the beginning."):
                from utils.helpers import force_page_reload
                force_page_reload()
        with b_col2:
            if st.button("Edit Details", use_container_width=True, help="Edit the plan details for the current incumbent."):
                st.session_state.editing_incumbent = True
                st.rerun()
