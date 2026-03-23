import Navbar from "../components/Navbar";
import { useEffect,useState } from "react";




export default function Dashboard() {

  const [cameraOpen, setCameraOpen] = useState(false);
  const [bodyVisible, setBodyVisible] = useState(false);
  const [cameraMode, setCameraMode] = useState("idle");
  const [isExercising, setIsExercising] = useState(false);

//   useEffect(() => {
//   if (!cameraOpen) return;

//   const interval = setInterval(async () => {
//     const res = await fetch("http://localhost:8000/body-visible");
//     const data = await res.json();
//     setBodyVisible(data.body_visible);
//   }, 500); // poll twice per second

//   return () => clearInterval(interval);
// }, [cameraOpen]);


  return (
    <>
      <Navbar />

      <div style={styles.container}>
        {/* LEFT PANEL */}
        <div style={styles.leftPanel}>
          {/* CALIBRATION */}
          <div style={styles.card}>
            <h3>Calibration</h3>
            <p>
              Calibrate to match your body proportions before
              exercising.
            </p>
            <button
              style={styles.primaryBtn}
              onClick={async () => {
                const token = localStorage.getItem("token");

                if (!token) {
                  alert("Please login first");
                  return;
                }

              
                await fetch("http://localhost:8000/set-token", {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                  },
                  body: JSON.stringify({
                    token: token,
                  }),
                });

                await fetch("http://localhost:8000/start-calibration", {
                  method: "POST",
                });

                setCameraOpen(true);
                setCameraMode("calibration");
              }}
                          >
              Start Calibration
            </button>

          </div>
          
          {/* EXERCISES */}
          <div style={styles.card} >
            <h3>Exercises</h3>
            <p>Select an exercise to begin posture analysis.</p>

            <button
              style={styles.exerciseBtn}
              onClick={async () => {
                await fetch("http://localhost:8000/start-exercise", { method: "POST" });
                setCameraOpen(true);
                setCameraMode("exercise");
              }}
            >
              Squats
            </button>

          </div>
        </div>

        
        {/* CAMERA SECTION */}
        <div style={styles.cameraSection}>
          <div style={styles.cameraBox}>
            <h2>Camera Feed</h2>
            <p style={{ opacity: 0.7 }}>
              Ensure your full body is visible in the camera frame
            </p>

            {cameraOpen ? (
  <>
    <div style={styles.cameraFeedWrapper}>
      <img
        key={cameraOpen}
        src="http://localhost:8000/video-feed"
        alt="Camera Feed"
        style={styles.cameraFeed}
      />

      {/* {!bodyVisible && (
        <div style={styles.overlay}>
          <div style={styles.overlayContent}>
            <span style={{ fontSize: "28px" }}>🧍</span>
            <p style={{ marginTop: "8px", fontWeight: "bold" }}>
              Body not fully visible
            </p>
            <p style={{ fontSize: "14px", opacity: 0.8 }}>
              Adjust your camera position
            </p>
          </div>
        </div>
      )} */}
    </div>

    

    <button
      
      style={styles.closeCameraBtn}
      onClick={async () => {
        await fetch("http://localhost:8000/stop-camera", { method: "POST" });
        setCameraOpen(false);
        setIsExercising(false); 
        setCameraMode("idle");
        window.location.reload();
        // setTimeout(() => setCameraOpen(true), 200);
      }}
    >
      {cameraMode === "calibration"
    ? "Stop Calibration"
    : cameraMode === "exercise"
    ? "Stop Exercising"
    : "Close Camera"}

    </button>
  </>
) : (
  <button
    style={styles.cameraBtn}
    onClick={() => setCameraOpen(true)}
  >
    Open Camera
  </button>
)}

          </div>
        </div>

      </div>
    </>
  );
}



const styles = {
  container: {
    marginTop: "90px",
    display: "flex",
    padding: "40px",
    gap: "40px",
    height: "calc(100vh - 90px)",
  },

  leftPanel: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    gap: "30px",
  },

  card: {
    background: "#1a2a32",
    borderRadius: "20px",
    padding: "25px",
    marginTop: "50px",
    marginBottom: "130px",
    boxShadow: "0 10px 30px rgba(0,0,0,0.3)",
  },

  primaryBtn: {
    marginTop: "15px",
    padding: "12px 28px",
    borderRadius: "30px",
    background: "linear-gradient(90deg, #56ab2f, #a8e063)",
    fontWeight: "bold",
  },

  exerciseBtn: {
    marginTop: "15px",
    padding: "12px 24px",
    borderRadius: "14px",
    background: "#56ab2f",
    fontWeight: "bold",
  },

  cameraSection: {
    flex: 1.2,
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },

  closeCameraBtn: {
  marginTop: "15px",
  padding: "12px 28px",
  borderRadius: "30px",
  background: "#ff4d4d",
  color: "white",
  fontWeight: "bold",
},


  cameraBox: {
    width: "100%",
    height: "100%",
    borderRadius: "25px",
    border: "2px dashed #56ab2f",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    gap: "20px",
  },

  cameraBtn: {
    padding: "14px 34px",
    borderRadius: "30px",
    background: "#a8e063",
    fontWeight: "bold",
    fontSize: "16px",
  },

  cameraFeedWrapper: {
  position: "relative",
  width: "100%",
  marginTop: "15px",
},

cameraFeed: {
  width: "100%",
  borderRadius: "20px",
},

overlay: {
  position: "absolute",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  background: "rgba(0, 0, 0, 0.55)",
  borderRadius: "20px",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
},

overlayContent: {
  textAlign: "center",
  color: "#fff",
  background: "rgba(0, 0, 0, 0.6)",
  padding: "20px 28px",
  borderRadius: "16px",
},

secondaryBtn: {
  marginTop: "10px",
  padding: "10px 22px",
  borderRadius: "20px",
  background: "#f1c40f",
  fontWeight: "bold",
},

};
