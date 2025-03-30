import React, { useState, useEffect } from "react";

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:5000/stats", {
      method: "GET",
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    })
      .then((res) => res.json())
      .then((data) => setStats(data));
  }, []);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">📊 Tableau de Bord</h2>
        <input
          type="text"
          placeholder="🔍 Rechercher..."
          className="search-input"
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats ? (
          <>
            <div className="card">
              <h3 className="text-lg font-semibold">📊 Politiques de sécurité</h3>
              <p className="text-2xl">{stats.policies}</p>
            </div>
            <div className="card">
              <h3 className="text-lg font-semibold">🔐 Alertes de sécurité</h3>
              <p className="text-2xl">{stats.alerts}</p>
            </div>
            <div className="card">
              <h3 className="text-lg font-semibold">🛡️ Score de sécurité</h3>
              <p className="text-2xl">{stats.securityScore}%</p>
            </div>
          </>
        ) : (
          <p className="text-center text-lg font-semibold">Chargement des données...</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
