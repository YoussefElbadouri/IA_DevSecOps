import React from "react";
import { Link } from "react-router-dom";
import { FaHome, FaShieldAlt, FaChartLine, FaSignOutAlt, FaTools, FaBug, FaCheckCircle, FaChartBar, FaDollarSign } from "react-icons/fa";

const Sidebar = ({ handleLogout }) => {
  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col p-5">
      <h1 className="text-xl font-bold text-center mb-6">AI Security</h1>
      <nav className="space-y-4">
        <Link to="/" className="flex items-center p-2 rounded hover:bg-gray-700">
          <FaHome className="mr-3 text-lg" /> Dashboard
        </Link>
        <Link to="/generate-policy" className="flex items-center p-2 rounded hover:bg-gray-700">
          <FaTools className="mr-3 text-lg" /> Génération de Politiques
        </Link>
        <Link to="/scan" className="flex items-center p-2 rounded hover:bg-gray-700">
          <FaBug className="mr-3 text-lg" /> Analyse de Vulnérabilités
        </Link>
        <Link to="/compliance" className="flex items-center p-2 rounded hover:bg-gray-700">
          <FaCheckCircle className="mr-3 text-lg" /> Validation & Conformité
        </Link>
        <Link to="/risks" className="flex items-center p-2 rounded hover:bg-gray-700">
          <FaChartBar className="mr-3 text-lg" /> Monitoring des Risques
        </Link>
        <Link to="/pricing" className="flex items-center p-2 rounded hover:bg-gray-700">
          <FaDollarSign className="mr-3 text-lg" /> Tarification
        </Link>
        <button onClick={handleLogout} className="flex items-center p-2 w-full rounded hover:bg-red-700 text-left">
          <FaSignOutAlt className="mr-3 text-lg" /> Déconnexion
        </button>
      </nav>
    </div>
  );
};

export default Sidebar;
