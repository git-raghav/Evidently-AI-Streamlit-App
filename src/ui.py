import os
from pathlib import Path
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components
from typing import Iterable
from typing import List
from typing import Text

from src.utils import EntityNotFoundError
from src.utils import get_report_name
from src.utils import period_dir_to_dates_range


def set_page_container_style() -> None:
    """Set report container style."""

    st.markdown("""
        <style>
            /* Main area styling */
            .main > div {
                max-width: 100%;
                padding: 1rem 2rem;
            }

            /* Tabs styling */
            button[data-baseweb="tab"] div p {
                font-size: 16px;
                font-weight: 600;
            }

            /* Sidebar styling */
            .css-1d391kg {
                padding: 2rem 1rem;
            }

            /* Selectbox styling */
            .stSelectbox {
                margin-bottom: 1.5rem;
            }

            /* Header styling */
            .stHeader {
                background-color: #f8f9fa;
                padding: 1.5rem;
                border-radius: 0.5rem;
                margin-bottom: 2rem;
            }

            /* Caption styling */
            .stCaption {
                font-size: 1rem;
                color: #6c757d;
                margin-bottom: 0.5rem;
            }

            /* Report container styling */
            .stReport {
                background-color: white;
                border-radius: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 1rem;
            }

            /* Sidebar link styling */
            .sidebar-link {
                display: inline-block;
                text-align: center;
                width: 100%;
                padding: 0.75rem;
                margin: 0.5rem 0;
                border-radius: 0.5rem;
                text-decoration: none;
                background-color: #f8f9fa;
                color: #1f2937;
                font-weight: 500;
                transition: all 0.2s ease;
            }

            .sidebar-link:hover {
                background-color: #e5e7eb;
                transform: translateY(-1px);
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }

            /* Logo container styling */
            .logo-container {
                margin-bottom: 2rem;
                padding: 1rem;
                background-color: white;
                border-radius: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    """, unsafe_allow_html=True)


def display_sidebar_header() -> None:
    # Logo
    logo = Image.open("static/logo.png")
    with st.sidebar:
        # Logo container with styling
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image(logo, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        repo_link = "https://github.com/mnrozhkov/evidently/tree/main/examples/integrations"
        evidently_docs = "https://docs.evidentlyai.com/"

        st.markdown(
            f'<a class="sidebar-link" href="{repo_link}" target="_blank">📚 Source code</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<a class="sidebar-link" href="{evidently_docs}" target="_blank">📖 Evidently docs</a>',
            unsafe_allow_html=True
        )

        st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)


def select_project(projects: List[Text]) -> Path:
    """Select a project name form selectbox
    and return path to the project directory.

    Args:
        projects (List[Text]): List of available projects.

    Raises:
        EntityNotFoundError: If projects list is empty.

    Returns:
        Path: Path to the project.
    """

    if not projects:
        raise EntityNotFoundError("🔍 Projects not found")

    selected_project: Text = st.sidebar.selectbox(
        label="💼 Select project", options=projects
    )

    return Path(selected_project)


def select_period(periods: List[Text]) -> Text:
    """

    Args:
        periods (List[Text]): List of period strings.

    Raises:
        EntityNotFoundError: If periods list is empty.

    Returns:
        Text: Dates period in format '%Y-%m-%d - %Y-%m-%d'.
    """
    if not periods:
        raise EntityNotFoundError("🔍 No periods found")

    selected_period: Text = st.sidebar.selectbox(
        label="📆 Select period", options=periods, format_func=period_dir_to_dates_range
    )

    return selected_period


def select_report(report_names: List[Text]) -> Text:
    """Select a report name from a selectbox.

    Args:
        report_names (List[Text]): Available report names.

    Raises:
        EntityNotFoundError: If report name list is empty.

    Returns:
        Text: Report name.
    """

    if not report_names:
        raise EntityNotFoundError("🔍 Reports not found")

    selected_report_name: Text = st.sidebar.selectbox(
        label="📈 Select report", options=report_names
    )

    return selected_report_name


def display_header(project_name: Text, period: Text, report_name: Text) -> None:
    """Display report header."""
    dates_range: Text = period_dir_to_dates_range(period)

    st.markdown('<div class="stHeader">', unsafe_allow_html=True)
    st.caption(f"💼 Project: {project_name}")
    st.header(f"📊 {report_name}")
    st.caption(f"📅 Period: {dates_range}")
    st.markdown('</div>', unsafe_allow_html=True)


@st.cache_data
def display_report(report_path: Path) -> List[Text]:
    """Display report."""

    st.markdown('<div class="stReport">', unsafe_allow_html=True)

    if report_path.is_file():
        with open(report_path, encoding="utf8") as report_f:
            report: Text = report_f.read()
            components.html(report, width=1000, height=800, scrolling=True)
        result = [report]

    elif report_path.is_dir():
        report_parts: List[Path] = sorted(
            list(map(
                lambda report_part: report_path / report_part,
                os.listdir(report_path))
            )
        )
        tab_names: List[Text] = map(get_report_name, report_parts)
        tab_names_formatted = [f"📈 {name}" for name in tab_names]

        tabs: Iterable[object] = st.tabs(tab_names_formatted)
        report_contents: List[Text] = []

        for tab, report_part_path in zip(tabs, report_parts):
            with tab:
                with open(report_part_path) as report_part_f:
                    report_part_content: Text = report_part_f.read()
                    report_contents.append(report_part_content)
                    components.html(
                        report_part_content, width=1000, height=800, scrolling=True
                    )
        result = report_contents
    else:
        result = EntityNotFoundError("🔍 No reports found")

    st.markdown('</div>', unsafe_allow_html=True)
    return result
