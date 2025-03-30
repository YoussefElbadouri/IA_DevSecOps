import React, { useState, useEffect } from "react";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js";
import { toast } from "react-toastify";

// 📊 Enregistrement des composants de Chart.js
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const RiskDashboard = () => {
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchRisks = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/risks", {
          method: "GET",
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        });

        const data = await response.json();
        console.log("📊 Données reçues :", data);

        if (!Array.isArray(data)) {
          throw new Error("Format inattendu des données");
        }

        setRisks(data);
      } catch (error) {
        console.error("❌ Erreur lors de la récupération des risques :", error);
        setError("Impossible de récupérer les risques");
        toast.error("Erreur lors du chargement des risques !");
      } finally {
        setLoading(false);
      }
    };

    fetchRisks();
  }, []);

  // 🎨 Configuration du graphique
  const chartData = {
    labels: risks.map(risk => risk.name),
    datasets: [
      {
        label: "Niveau de Risque (%)",
        data: risks.map(risk => risk.level),
        backgroundColor: "rgba(255, 99, 132, 0.5)", // 🔴 Couleur du graphique
        borderColor: "rgba(255, 99, 132, 1)",
        borderWidth: 1,
      }
    ],
  };

  return (
    <div className="container">
      <h2 className="text-2xl font-bold">📊 Dashboard de Risques</h2>

      {loading ? (
        <p>Chargement...</p>
      ) : error ? (
        <p className="text-red-500">{error}</p>
      ) : (
        <>
          <Bar data={chartData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
          <ul className="mt-4">
            {risks.map((risk, index) => (
              <li key={index} className="risk-item bg-gray-800 p-3 rounded-lg shadow-md">
                <strong>{risk.name}</strong>: <span className="text-red-400">{risk.level}%</span>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
};

export default RiskDashboard;
