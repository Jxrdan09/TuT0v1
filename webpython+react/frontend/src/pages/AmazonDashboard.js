import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { amazonAPI, proxyAPI } from '../services/api';
import { 
  CreditCard, 
  Cookie, 
  History, 
  BarChart3,
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  Settings,
  Trash2,
  Play,
  Globe
} from 'lucide-react';
import toast from 'react-hot-toast';

const AmazonDashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('checker');
  const [cookie, setCookie] = useState('');
  const [cardData, setCardData] = useState('');
  const [multipleCards, setMultipleCards] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [proxyStats, setProxyStats] = useState({});
  const [history, setHistory] = useState([]);
  const [hasCookie, setHasCookie] = useState(false);

  useEffect(() => {
    checkCookieStatus();
    loadStats();
    loadHistory();
    loadProxyStats();
  }, []);

  const checkCookieStatus = async () => {
    try {
      const response = await amazonAPI.getCookie();
      setHasCookie(true);
      setCookie(response.data.cookie_data);
    } catch (error) {
      setHasCookie(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await amazonAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error cargando estadísticas:', error);
    }
  };

  const loadProxyStats = async () => {
    try {
      const response = await proxyAPI.getUserStats();
      setProxyStats(response.data);
    } catch (error) {
      console.error('Error cargando estadísticas de proxies:', error);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await amazonAPI.getHistory();
      setHistory(response.data);
    } catch (error) {
      console.error('Error cargando historial:', error);
    }
  };

  const saveCookie = async () => {
    if (!cookie.trim()) {
      toast.error('La cookie no puede estar vacía');
      return;
    }

    setLoading(true);
    try {
      await amazonAPI.saveCookie({
        gateway_type: 'amazon',
        cookie_data: cookie
      });
      toast.success('Cookie guardada exitosamente');
      setHasCookie(true);
    } catch (error) {
      toast.error('Error al guardar la cookie');
    } finally {
      setLoading(false);
    }
  };

  const deleteCookie = async () => {
    if (!window.confirm('¿Estás seguro de que quieres eliminar la cookie?')) {
      return;
    }

    try {
      await amazonAPI.deleteCookie();
      toast.success('Cookie eliminada exitosamente');
      setHasCookie(false);
      setCookie('');
    } catch (error) {
      toast.error('Error al eliminar la cookie');
    }
  };

  const checkSingleCard = async () => {
    if (!cardData.trim()) {
      toast.error('Ingresa los datos de la tarjeta');
      return;
    }

    if (!hasCookie) {
      toast.error('Primero debes configurar una cookie');
      return;
    }

    setLoading(true);
    try {
      await amazonAPI.checkCard({
        card_data: cardData,
        cookie: cookie
      });
      
      toast.success('Tarjeta verificada');
      loadHistory();
      loadStats();
    } catch (error) {
      toast.error('Error al verificar la tarjeta');
    } finally {
      setLoading(false);
    }
  };

  const checkMultipleCards = async () => {
    if (!multipleCards.trim()) {
      toast.error('Ingresa las tarjetas');
      return;
    }

    if (!hasCookie) {
      toast.error('Primero debes configurar una cookie');
      return;
    }

    const cards = multipleCards.split('\n').filter(card => card.trim());
    if (cards.length > 15) {
      toast.error('Máximo 15 tarjetas por consulta');
      return;
    }

    setLoading(true);
    try {
      await amazonAPI.checkMultipleCards(cards);
      toast.success('Tarjetas verificadas');
      loadHistory();
      loadStats();
    } catch (error) {
      toast.error('Error al verificar las tarjetas');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'declined':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'error':
      case 'invalid_cookies':
      case 'api_error':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'declined':
        return 'bg-red-100 text-red-800';
      case 'error':
      case 'invalid_cookies':
      case 'api_error':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const tabs = [
    { id: 'checker', name: 'Verificador', icon: CreditCard },
    { id: 'cookie', name: 'Cookie', icon: Cookie },
    { id: 'history', name: 'Historial', icon: History },
    { id: 'stats', name: 'Estadísticas', icon: BarChart3 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Amazon Gateway</h1>
        <p className="text-gray-600">
          Verifica tarjetas de crédito en Amazon Global
        </p>
      </div>

      {/* Status de Cookie */}
      <div className={`p-4 rounded-lg ${hasCookie ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
        <div className="flex items-center">
          <Cookie className={`h-5 w-5 mr-2 ${hasCookie ? 'text-green-600' : 'text-red-600'}`} />
          <span className={`font-medium ${hasCookie ? 'text-green-800' : 'text-red-800'}`}>
            {hasCookie ? 'Cookie configurada' : 'Cookie no configurada'}
          </span>
        </div>
        {!hasCookie && (
          <p className="text-red-600 text-sm mt-1">
            Debes configurar una cookie de Amazon para usar el verificador
          </p>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm inline-flex items-center ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'checker' && (
        <div className="space-y-6">
          {/* Verificador de tarjeta única */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Verificar Tarjeta Individual
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="form-label">
                  Datos de la Tarjeta (cc|mm|yyyy|cvv)
                </label>
                <input
                  type="text"
                  value={cardData}
                  onChange={(e) => setCardData(e.target.value)}
                  placeholder="1234567890123456|12|2025|123"
                  className="input-field"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Formato: número de tarjeta|mes|año|cvv
                </p>
              </div>
              
              <button
                onClick={checkSingleCard}
                disabled={loading || !hasCookie}
                className="btn-primary inline-flex items-center"
              >
                <Play className="h-4 w-4 mr-2" />
                {loading ? 'Verificando...' : 'Verificar Tarjeta'}
              </button>
            </div>
          </div>

          {/* Verificador de múltiples tarjetas */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Verificar Múltiples Tarjetas
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="form-label">
                  Tarjetas (una por línea, máximo 15)
                </label>
                <textarea
                  value={multipleCards}
                  onChange={(e) => setMultipleCards(e.target.value)}
                  placeholder="1234567890123456|12|2025|123&#10;1234567890123457|01|2026|456"
                  className="input-field h-32 resize-none"
                  rows={6}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Una tarjeta por línea. Formato: cc|mm|yyyy|cvv
                </p>
              </div>
              
              <button
                onClick={checkMultipleCards}
                disabled={loading || !hasCookie}
                className="btn-primary inline-flex items-center"
              >
                <Play className="h-4 w-4 mr-2" />
                {loading ? 'Verificando...' : 'Verificar Tarjetas'}
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'cookie' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Configuración de Cookie
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="form-label">
                Cookie de Amazon
              </label>
              <textarea
                value={cookie}
                onChange={(e) => setCookie(e.target.value)}
                placeholder="Pega aquí tu cookie de Amazon..."
                className="input-field h-32 resize-none"
                rows={6}
              />
              <p className="text-xs text-gray-500 mt-1">
                Obtén tu cookie desde las herramientas de desarrollador de tu navegador
              </p>
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={saveCookie}
                disabled={loading}
                className="btn-primary inline-flex items-center"
              >
                <Settings className="h-4 w-4 mr-2" />
                {loading ? 'Guardando...' : 'Guardar Cookie'}
              </button>
              
              {hasCookie && (
                <button
                  onClick={deleteCookie}
                  className="btn-danger inline-flex items-center"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Eliminar Cookie
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'history' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Historial de Verificaciones
          </h2>
          
          {history.length === 0 ? (
            <div className="text-center py-8">
              <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No hay verificaciones aún</p>
            </div>
          ) : (
            <div className="space-y-3">
              {history.map((check) => (
                <div
                  key={check.id}
                  className="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(check.status)}
                    <div>
                      <p className="font-medium text-gray-900">
                        {check.card_number}
                      </p>
                      <p className="text-sm text-gray-500">
                        {new Date(check.created_at).toLocaleString()}
                        {check.proxy_used && (
                          <span className="ml-2 text-indigo-500">
                            • Proxy: {check.proxy_used.split(':')[0]}:{check.proxy_used.split(':')[1]}
                          </span>
                        )}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(check.status)}`}>
                      {check.status}
                    </span>
                    {check.processing_time && (
                      <span className="text-xs text-gray-500">
                        {check.processing_time.toFixed(2)}s
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'stats' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          <div className="card">
            <div className="flex items-center">
              <CreditCard className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Verificaciones</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stats?.total_checks || 0}
                </p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Aprobadas</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stats?.approved || 0}
                </p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <XCircle className="h-8 w-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Rechazadas</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stats?.declined || 0}
                </p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <BarChart3 className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Tasa de Éxito</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stats?.success_rate?.toFixed(1) || 0}%
                </p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <Globe className="h-8 w-8 text-indigo-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Proxies Usados</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {proxyStats?.unique_proxies_used || 0}
                </p>
                <p className="text-xs text-indigo-600">
                  {proxyStats?.total_checks_with_proxy || 0} verificaciones con proxy
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AmazonDashboard;
