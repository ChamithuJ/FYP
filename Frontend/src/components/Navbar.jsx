import React from "react";
import { useNavigate } from "react-router-dom";



export default function Navbar() {

  const navigate = useNavigate();
  const handleLogout = async () => {
    const token = localStorage.getItem("token");

    try {
      // Optional: call backend logout
      await fetch("http://localhost:8000/logout", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    } catch (err) {
      console.log("Logout API failed (not critical)", err);
    }

    // Clear frontend session
    localStorage.removeItem("token");

    // Redirect to login page
    navigate("/login");
  };



  return (
    <div style={styles.nav}>
       <img src="/postura-logo.png" alt="POSTURA" style={styles.pict} />
        <h2 style={styles.logo}>DASHBOARD</h2>

      <div style={styles.links}>
        {/* <span>Dashboard</span> */}
        <span>Calibration</span>
        <span>Exercises</span>
        <span style={styles.logout} onClick={handleLogout}>
          Logout
        </span>
      </div>
    </div>
  );
}

const styles = {
  nav: {
    height: "70px",
    width: "100%",
    position: "fixed",
    top: 0,
    left: 0,
    background: "#0f2027",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 40px",
    zIndex: 1000,
  },
   pict: {
    height: "50px",
    borderRadius: "8px",
  },
  logo: {
  //  color: "#56ab2f",
    margin: 0,
  },
  links: {
    display: "flex",
    gap: "30px",
    cursor: "pointer",
    fontWeight: "500",
  },

  logout: {
    cursor: "pointer",
    color: "#ff4d4d",
    fontWeight: "bold",
  },
};
