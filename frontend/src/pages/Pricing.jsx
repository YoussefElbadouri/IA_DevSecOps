import React from "react";

const Pricing = () => {
  return (
      <div>
          <h1>Nos Tarifs</h1>
          <div className="grid grid-rows-2 grid-cols-2  gap-6">
              <div className="card">
                  <h3>Starter</h3>
                  <p>💲 19€/mois</p>
                  <p>Analyse de base</p>
                  <p>1 scan/mois</p>
                  <button className="btn btn-primary">Choisir</button>
              </div>

              <div className="card">
                  <h3>Pro</h3>
                  <p>💲 49€/mois</p>
                  <p>Scans illimités</p>
                  <p>Dashboard avancé</p>
                  <button className="btn btn-primary">Choisir</button>
              </div>
          </div>
      </div>

  );
};

export default Pricing;
