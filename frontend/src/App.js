import React, { useEffect, useState } from "react";
import axios from "axios";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

function App() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/stats")
      .then(response => {
        setStats(response.data);
      })
      .catch(error => {
        console.error("Error fetching stats:", error);
      });
  }, []);

  if (!stats) {
    return <h2>Loading...</h2>;
  }

  const data = {
    labels: ["Positive", "Negative", "Neutral"],
    datasets: [
      {
        label: "Sentiment Distribution",
        data: [stats.positive, stats.negative, stats.neutral],
        backgroundColor: [
          "green",
          "red",
          "gray"
        ]
      }
    ]
  };

  return (
    <div style={{ width: "600px", margin: "50px auto", textAlign: "center" }}>
      <h1>COVID Tweet Sentiment Dashboard</h1>
      <h3>Total Tweets: {stats.total}</h3>
      <Pie data={data} />
    </div>
  );
}

export default App;