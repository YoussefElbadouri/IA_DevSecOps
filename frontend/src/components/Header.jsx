import React from "react";
import { FaUser, FaSignOutAlt } from "react-icons/fa";

const Header = ({ isAuthenticated, user, handleLogout }) => {
  console.log("User in Header:", user); // Debugging

  return isAuthenticated ? (
    <header className="flex items-center justify-between bg-white p-4 shadow-md">
      <h2 className="text-lg font-semibold text-gray-700">Tableau de Bord</h2>
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <FaUser className="text-black" />
          <span className="text-black font-semibold">
            {user?.name ? user.name : "Utilisateur"}
          </span>
        </div>
        <button onClick={handleLogout} className="p-2 rounded-full hover:bg-red-200 text-red-600 transition">
          <FaSignOutAlt />
        </button>
      </div>
    </header>
  ) : null;
};

export default Header;
