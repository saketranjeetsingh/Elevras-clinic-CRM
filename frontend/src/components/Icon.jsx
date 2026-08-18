function Icon({ name, size = 18, className = "" }) {
    const icons = {
        dashboard: (
            <path d="M4 4h7v7H4zM13 4h7v4h-7zM13 10h7v10h-7zM4 13h7v7H4z" />
        ),
        patients: (
            <path d="M16 8a3 3 0 1 0-3-3 3 3 0 0 0 3 3Zm-8 0a3 3 0 1 0-3-3 3 3 0 0 0 3 3Zm0 2c-2.8 0-5 1.6-5 3.6V16h10v-2.4C13 11.6 10.8 10 8 10Zm8 0c-.7 0-1.4.1-2 .3a4.2 4.2 0 0 1 0 3.7c1.4.4 2 1 2 1.6V16h4v-2.4c0-2-2.2-3.6-4-3.6Z" />
        ),
        import: (
            <path d="M12 2 4 6v3h2V7l6-3 6 3v2h2V6Zm-1 8v6h2v-6h3l-4-4-4 4Zm-8 2v6a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-6h-2v6H5v-6Z" />
        ),
        appointments: (
            <path d="M7 3v2H5a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2V3h-2v2H9V3Zm12 6H5v9h14Z" />
        ),
        treatments: (
            <path d="M12 2a7 7 0 0 0-7 7c0 2.8 1.7 5.2 4.2 6.3V20h5.6v-4.7A7 7 0 0 0 19 9a7 7 0 0 0-7-7Zm0 4.6a2.4 2.4 0 1 1-2.4 2.4A2.4 2.4 0 0 1 12 6.6Z" />
        ),
        bills: (
            <path d="M4 5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v14l-3-2-3 2-3-2-3 2-3-2Zm4 3h8v2H8Zm0 4h8v2H8Z" />
        ),
        medical: (
            <path d="M12 2 4 6v6c0 5 3.4 8.7 8 10 4.6-1.3 8-5 8-10V6Zm-1 5h2v3h3v2h-3v3h-2v-3H8v-2h3Z" />
        ),
        timeline: (
            <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2Zm1 5h-2v6l5 3 1-1.7-4-2.3Z" />
        ),
        actions: (
            <path d="M5 4h14a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1h-4l-2 4-2-4H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Zm2 3v2h10V7Z" />
        ),
        calendar: (
            <path d="M7 2h2v2h6V2h2v2h3v16H4V4h3Zm12 6H5v10h14Z" />
        ),
        activity: (
            <path d="M5 12h4l2-5 3 10 2-5h3" />
        ),
        followup: (
            <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2Zm1 5h-2v6l5 3 1-1.7-4-2.3Z" />
        ),
        check: (
            <path d="M20 6 9 17l-5-5 1.4-1.4 3.6 3.6 9.6-9.6Z" />
        ),
        alert: (
            <path d="M12 2 1 21h22Zm0 5 6 11H6Zm-1 3v4h2v-4Zm0 6v2h2v-2Z" />
        ),
        profile: (
            <path d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-3.3 0-6 1.8-6 4v2h12v-2c0-2.2-2.7-4-6-4Z" />
        ),
        plus: (
            <path d="M11 5h2v6h6v2h-6v6h-2v-6H5v-2h6Z" />
        ),
        search: (
            <path d="M10 4a6 6 0 1 1 0 12 6 6 0 0 1 0-12Zm8 12 3 3-1.4 1.4-3-3" />
        ),
        sun: (
            <g>
                <circle cx="12" cy="12" r="4" />
                <path
                    d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    fill="none"
                />
            </g>
        ),
        moon: (
            <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
        ),
        logout: (
            <path d="M4 4h8v16H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Zm11.6 3.6 1.6 2.4H9v2h8.2l-1.6 2.4 1.6 1.2L21 12l-3.8 4.4-1.6-1.2 1.6-2.4H9v-2h8.2l-1.6-2.4Z" />
        ),
    };

    return (
        <svg
            className={className}
            viewBox="0 0 24 24"
            width={size}
            height={size}
            fill="currentColor"
            aria-hidden="true"
        >
            {icons[name] || icons.dashboard}
        </svg>
    );
}

export default Icon;
