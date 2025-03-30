import React, { useState } from "react";
import { toast } from "react-toastify";

const PoliciesGenerator = () => {
  const [policy, setPolicy] = useState("");

  const generatePolicy = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/generate-policy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ policyType: "cybersecurity" }),
      });

      const data = await response.json();
      setPolicy(data.policy);
      toast.success("Politique générée avec succès !");
    } catch (error) {
      toast.error("Erreur lors de la génération !");
    }
  };

  return (
    <div className="container">
      <h2>📜 Génération de Politiques de Sécurité</h2>
      <button className="btn btn-primary" onClick={generatePolicy}>Générer</button>
      {policy && <textarea value={policy} readOnly className="policy-box" />}
    </div>
  );
};

export default PoliciesGenerator;
