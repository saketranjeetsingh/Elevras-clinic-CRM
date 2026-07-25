function MedicalHistoryCard({ medicalHistoryItems }) {
    return (
        <section className="section-card">
            <div className="section-heading-row">
                <h2>Medical History</h2>
            </div>
            {medicalHistoryItems.length > 0 ? (
                <div className="medical-history-list">
                    {medicalHistoryItems.map((item) => (
                        <span className="medical-history-pill" key={item}>{item}</span>
                    ))}
                </div>
            ) : (
                <p className="empty-state">No medical history recorded.</p>
            )}
        </section>
    );
}

export default MedicalHistoryCard;
