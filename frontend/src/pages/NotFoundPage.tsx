import React from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';
import './NotFoundPage.css';

const NotFoundPage: React.FC = () => {
  return (
    <div className="not-found-page">
      <div className="not-found-content">
        <div className="br-card">
          <div className="card-content">
            <AlertTriangle size={64} className="error-icon" />
            <div className="error-code">404</div>
            <h2 className="error-title">Página não encontrada</h2>
            <p className="error-description">
              A página que você está procurando não existe ou foi movida.
              Verifique o URL ou volte para a página inicial para continuar navegando.
            </p>
            <Link to="/" className="home-button">
              Voltar para o início
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;