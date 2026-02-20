export default function Navbar() {
  return (
    <div style={styles.nav}>
       <img src="/postura-logo.png" alt="POSTURA" style={styles.pict} />
        <h2 style={styles.logo}>DASHBOARD</h2>

      <div style={styles.links}>
        {/* <span>Dashboard</span> */}
        <span>Calibration</span>
        <span>Exercises</span>
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
};
