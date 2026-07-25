function PatientTimeline({ timelineItems, formatDateLabel }) {
    return (
        <section className="section-card">
            <div className="section-heading-row">
                <h2>Patient Timeline</h2>
            </div>
            {timelineItems.length === 0 ? (
                <p className="empty-state">No timeline events yet.</p>
            ) : (
                <div className="timeline-list">
                    {timelineItems.map((item) => (
                        <div className="timeline-item" key={item.id}>
                            <div className="timeline-icon">{item.icon}</div>
                            <div className="timeline-content">
                                <div className="timeline-meta">
                                    <strong className="timeline-title">{item.title}</strong>
                                    <span className="status-badge neutral">{item.badge}</span>
                                </div>
                                <p className="timeline-date">{formatDateLabel(item.date)}</p>
                                <p className="timeline-description">{item.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </section>
    );
}

export default PatientTimeline;
