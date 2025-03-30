import React from "react";

const SecurityCard = () => {
  return (
    <div className="bg-white shadow p-4 rounded-lg">
      <h3 className="text-xl font-semibold mb-2">Score de Sécurité</h3>
      <div className="text-4xl font-bold text-green-500">82/100</div>
      <p className="text-gray-600">Basé sur la dernière analyse</p>
    </div>
  );
};

export default SecurityCard;
