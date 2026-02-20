import { useNavigate } from "react-router-dom";
import { useState } from "react";

export default function Signup() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSignup = () => {
    if (username && password) {
      navigate("/login");
    } else {
      alert("Please fill all fields");
    }
  };

  return (
    <div style={styles.container}>
      <h1>Sign Up</h1>

      <input
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        style={styles.input}
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={styles.input}
      />

      <button style={styles.button} onClick={handleSignup}>
        Create Account
      </button>

      <p style={styles.link} onClick={() => navigate("/login")}>
        Already have an account? Login
      </p>
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
    gap: "16px",
  },
  input: {
    width: "260px",
    padding: "12px",
    borderRadius: "10px",
    border: "none",
  },
  button: {
    padding: "12px 30px",
    borderRadius: "30px",
    background: "#a8e063",
    fontWeight: "bold",
  },
  link: {
    marginTop: "10px",
    cursor: "pointer",
    opacity: 0.8,
  },
};
