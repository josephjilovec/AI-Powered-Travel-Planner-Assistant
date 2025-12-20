"""
Mobile utility functions for responsive design.
"""

import streamlit as st


def is_mobile() -> bool:
    """
    Detect if the user is on a mobile device.
    
    Note: Streamlit doesn't provide direct access to screen width,
    but we can use CSS media queries and session state to approximate.
    
    Returns:
        Boolean indicating if mobile layout should be used.
    """
    # Check if mobile preference is set in session state
    if "is_mobile" in st.session_state:
        return st.session_state.is_mobile
    
    # Default to responsive columns that stack on mobile
    # Streamlit columns automatically stack on narrow screens
    return False


def get_column_count() -> int:
    """
    Get the number of columns to use based on screen size.
    
    Returns:
        Number of columns (2 for desktop, 1 for mobile).
    """
    if is_mobile():
        return 1
    return 2


def apply_mobile_css() -> None:
    """Apply CSS for mobile responsiveness."""
    st.markdown(
        """
        <style>
        /* Mobile-responsive styles */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem;
            }
            
            .stButton>button {
                width: 100%;
                margin-bottom: 0.5rem;
            }
            
            /* Stack columns on mobile */
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
            }
        }
        
        /* Ensure buttons are full width on mobile */
        @media (max-width: 768px) {
            .element-container {
                width: 100% !important;
            }
        }
        
        /* Better spacing for mobile */
        .main {
            padding-top: 1rem;
        }
        
        /* Responsive text */
        @media (max-width: 768px) {
            h1 {
                font-size: 1.5rem !important;
            }
            h2 {
                font-size: 1.25rem !important;
            }
            h3 {
                font-size: 1.1rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

