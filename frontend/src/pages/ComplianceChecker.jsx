import React, { useState } from "react";
import { toast } from "react-toastify";

const ComplianceChecker = () => {
  const [result, setResult] = useState(null);

  const checkCompliance = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/compliance-check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ framework: "NIST" }),
      });

      const data = await response.json();
      setResult(data);
      toast.success("Vérification terminée !");
    } catch (error) {
      toast.error("Erreur lors de la vérification !");
    }
  };

  return (
    <div className="container">
      <h2>✅ Validation et Conformité</h2>
      <button className="btn btn-success" onClick={checkCompliance}>Vérifier</button>
      {result && <pre className="result-box">{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
};

export default ComplianceChecker;
