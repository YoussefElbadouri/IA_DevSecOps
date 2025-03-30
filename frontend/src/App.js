import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Dashboard from "./components/Dashboard";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Policies from "./pages/Policies";
import Alerts from "./pages/Alerts";
import PoliciesGenerator from "./pages/PoliciesGenerator";
import VulnerabilityScanner from "./pages/VulnerabilityScanner";
import ComplianceChecker from "./pages/ComplianceChecker";
import RiskDashboard from "./pages/RiskDashboard";
import Pricing from "./pages/Pricing";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(true);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem("token");
      const tokenExpiration = localStorage.getItem("token_expiration");
      const storedUser = localStorage.getItem("user");

      console.log("🔍 Vérification Auth - Token:", token, "Expiration:", tokenExpiration, "User:", storedUser);

      if (token && tokenExpiration && Date.now() < parseInt(tokenExpiration)) {
        setIsAuthenticated(true);
        if (storedUser) {
          setUser(JSON.parse(storedUser));
        }
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
      setLoadingAuth(false); // ⏳ Fin du chargement
    };

    setTimeout(checkAuth, 500); // ✅ Ajoute un léger délai avant la vérification

    window.addEventListener("storage", checkAuth);
    return () => window.removeEventListener("storage", checkAuth);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("token_expiration");
    localStorage.removeItem("user");
    setIsAuthenticated(false);
    setUser(null);
    toast.success("Déconnexion réussie", { position: "top-right", autoClose: 3000 });
  };

  // ⏳ Affichage d'un écran de chargement pendant la vérification
  if (loadingAuth) {
    return (
      <div className="flex h-screen items-center justify-center text-white text-xl">
        Chargement...
      </div>
    );
  }

  return (
    <Router>
      <ToastContainer autoClose={3000} />
      <div className="flex h-screen bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white">
        {isAuthenticated && <Sidebar isAuthenticated={isAuthenticated} handleLogout={handleLogout} />}
        <div className="flex flex-col flex-1">
          {isAuthenticated && <Header isAuthenticated={isAuthenticated} user={user} handleLogout={handleLogout} />}
          <main className="p-6">
            <Routes>
              <Route path="/" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} />
              <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} setUser={setUser} />} />
              <Route path="/register" element={<Register />} />
              <Route path="/policies" element={isAuthenticated ? <Policies /> : <Navigate to="/login" />} />
              <Route path="/alerts" element={isAuthenticated ? <Alerts /> : <Navigate to="/login" />} />
              <Route path="/dashboard" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} />
              <Route path="/generate-policy" element={isAuthenticated ? <PoliciesGenerator /> : <Navigate to="/login" />} />
              <Route path="/scan" element={isAuthenticated ? <VulnerabilityScanner /> : <Navigate to="/login" />} />
              <Route path="/compliance" element={isAuthenticated ? <ComplianceChecker /> : <Navigate to="/login" />} />
              <Route path="/risks" element={isAuthenticated ? <RiskDashboard /> : <Navigate to="/login" />} />
              <Route path="/pricing" element={<Pricing />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
