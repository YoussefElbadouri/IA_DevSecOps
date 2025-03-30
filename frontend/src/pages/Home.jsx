import React from "react";
import SecurityCard from "../components/SecurityCard";
import AlertsList from "../components/AlertsList";

const Home = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Carte d'état de sécurité */}
      <SecurityCard />

      {/* Liste des alertes */}
      <AlertsList />
    </div>
  );
};

export default Home;
