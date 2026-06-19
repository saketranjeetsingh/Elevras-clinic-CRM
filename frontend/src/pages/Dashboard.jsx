function Dashboard() {

    const token =
        localStorage.getItem("token");

    return (

        <div>

            <h1>
                Dashboard
            </h1>

            <p>
                Logged In
            </p>

            <p>
                Token:
            </p>

            <textarea
                rows="10"
                cols="80"
                value={token || ""}
                readOnly
            />

        </div>
    );
}

export default Dashboard;