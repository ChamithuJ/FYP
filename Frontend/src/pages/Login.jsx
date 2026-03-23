import { useNavigate } from "react-router-dom";
import { useState } from "react";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");



  const handleLogin = async () => {
  if (!username || !password) {
    alert("Please enter username and password");
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.detail);
      return;
    }

    
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("username", username);

    alert("Login successful!");
    navigate("/dashboard");

  } catch (error) {
    console.error("Login error:", error);
    alert("Something went wrong");
  }
};

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Login</h1>

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

      <button style={styles.button} onClick={handleLogin}>
        Login
      </button>

      <p style={styles.link} onClick={() => navigate("/signup")}>
        Don’t have an account? Sign up
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
    title: {
    fontSize: "77px",
    marginBottom: "20px",

  },
  button: {
    padding: "12px 30px",
    borderRadius: "30px",
    background: "#56ab2f",
    fontWeight: "bold",
  },
  link: {
    marginTop: "10px",
    cursor: "pointer",
    opacity: 0.8,
  },
};
