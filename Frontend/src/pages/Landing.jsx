import { useNavigate } from "react-router-dom";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div style={styles.container}>
      <img src="/postura-logo.png" alt="POSTURA" style={styles.logo} />

      <h1 style={styles.title}>POSTURA</h1>
      <p>AI-Based Fitness Posture Checker</p>

      <button
        style={styles.button}
        onClick={() => navigate("/login")}
      >
        Get Started
      </button>
    </div>
  );
}

const styles = {
  container: {
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    gap: "20px",
    textAlign: "center",
  },
  logo: {
    width: "520px",
    borderRadius: "16px",
    marginTop: "-50px",
    marginBottom: "20px",
  },
    title: {
    fontSize: "80px",
    margin: "0",
  },
  button: {
    marginTop: "20px",
    padding: "14px 32px",
    fontSize: "16px",
    borderRadius: "30px",
    background: "linear-gradient(90deg, #56ab2f, #a8e063)",
    color: "#0f2027",
    fontWeight: "bold",
    cursor: "pointer",
  },
};


