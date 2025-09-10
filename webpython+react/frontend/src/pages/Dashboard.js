import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { gatesAPI } from '../services/api';
import { 
  BarChart3,
  Users,
  Play,
  CheckCircle,
  XCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { user } = useAuth();
  const [gates, setGates] = useState({});
  const [gateStats, setGateStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedGate, setSelectedGate] = useState(null);
  const [singleInput, setSingleInput] = useState('');
  const [results, setResults] = useState(null);
  const [isChecking, setIsChecking] = useState(false);

  useEffect(() => {
    fetchGatesData();
  }, []);

  // Función para usar un gate específico
  const handleGateClick = async (gateName) => {
    setSelectedGate(gateName);
    setResults(null);
    setSingleInput('');
  };

  // Un solo input: cada gateway define su formato en el backend; aquí solo enviamos la cadena

  // Función para verificar con el gate seleccionado
  const handleCheck = async () => {
    if (!selectedGate) {
      toast.error('Selecciona un gate primero');
      return;
    }

    if (!singleInput.trim()) {
      toast.error('Ingresa los datos en el campo');
      return;
    }

    setIsChecking(true);
    toast.loading(`Verificando con ${selectedGate}...`, { id: 'checking' });

    try {
      const result = await gatesAPI.checkGate(selectedGate, { input: singleInput });
      setResults(result);
      toast.success(`Verificación con ${selectedGate} completada`, { id: 'checking' });
    } catch (error) {
      toast.error(`Error al verificar con ${selectedGate}`, { id: 'checking' });
    } finally {
      setIsChecking(false);
    }
  };

  const fetchGatesData = async () => {
    try {
      const response = await gatesAPI.getAllGates();
      setGates(response.gates);
      setGateStats(response.global_stats);
    } catch (error) {
      console.error('Error al cargar datos de gates:', error);
      // Datos por defecto para gates
      setGates({
        IRIS: { id: 'IRIS', name: 'IRIS', type: 'auth', status: 'live' },
        KAIROS: { id: 'KAIROS', name: 'KAIROS', type: 'auth', status: 'dead' },
        DIONE: { id: 'DIONE', name: 'DIONE', type: 'auth', status: 'live' },
        HEBE: { id: 'HEBE', name: 'HEBE', type: 'auth', status: 'live' },
        PAYPAL: { id: 'PAYPAL', name: 'PAYPAL', type: 'charge', status: 'live' },
        HERMES: { id: 'HERMES', name: 'HERMES', type: 'auth', status: 'live' },
        AMAZON: { id: 'AMAZON', name: 'AMAZON', type: 'charge', status: 'live' }
      });
      setGateStats({ livesToday: 347, totalLives: 3738178 });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">
      {/* Sidebar con los gates */}
      <div className="w-48 bg-gray-900 text-white p-4 flex flex-col gap-2">
        <div className="mb-4">
          <h2 className="text-lg font-bold text-center">Gates</h2>
          <div className="text-xs text-gray-400 text-center">
            Lives Hoy: {gateStats?.livesToday || 0}
          </div>
        </div>
        
        {Object.values(gates).map((gate) => (
          <button
            key={gate.id}
            className={`px-3 py-2 rounded flex items-center justify-between ${
              gate.status === 'live'
                ? 'bg-green-600 hover:bg-green-700'
                : 'bg-red-600 hover:bg-red-700'
            } ${selectedGate === gate.name ? 'ring-2 ring-blue-400' : ''}`}
            onClick={() => handleGateClick(gate.name)}
          >
            <span>{gate.name}</span>
            <div className={`w-2 h-2 rounded-full ${
              gate.status === 'live' ? 'bg-green-300' : 'bg-red-300'
            }`}></div>
          </button>
        ))}
      </div>

      {/* Área principal */}
      <div className="flex-1 p-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              ¡Hola, {user?.username}!
            </h1>
            <p className="text-gray-600">
              {selectedGate ? `Verificando con ${selectedGate}` : 'Selecciona un gate para comenzar'}
            </p>
          </div>

          {selectedGate && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">{selectedGate}</h2>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Entrada</label>
                <input
                  type="text"
                  value={singleInput}
                  onChange={(e) => setSingleInput(e.target.value)}
                  placeholder={selectedGate === 'AMAZON' ? 'cc|mm|yyyy|cvv' : 'Datos para el gateway'}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                {selectedGate === 'AMAZON' && (
                  <p className="text-xs text-gray-500 mt-1">Formato: número|mes|año|cvv. Requiere cookie configurada en Amazon.</p>
                )}
              </div>
              <button
                onClick={handleCheck}
                disabled={isChecking}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg flex items-center"
              >
                <Play className="h-4 w-4 mr-2" />
                {isChecking ? 'Verificando...' : 'Verificar'}
              </button>
            </div>
          )}

          {/* Resultados */}
          {results && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Resultados de {selectedGate}
              </h2>
              
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <CheckCircle className="h-6 w-6 text-green-600 mr-2" />
                    <div>
                      <p className="text-sm font-medium text-green-800">Live CVV</p>
                      <p className="text-2xl font-bold text-green-900">
                        {results.results?.liveCVV || 0}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <CheckCircle className="h-6 w-6 text-blue-600 mr-2" />
                    <div>
                      <p className="text-sm font-medium text-blue-800">Live CNN</p>
                      <p className="text-2xl font-bold text-blue-900">
                        {results.results?.liveCNN || 0}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <XCircle className="h-6 w-6 text-red-600 mr-2" />
                    <div>
                      <p className="text-sm font-medium text-red-800">Dead</p>
                      <p className="text-2xl font-bold text-red-900">
                        {results.results?.dead || 0}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Estadísticas */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center">
                <BarChart3 className="h-8 w-8 text-green-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-500">Lives Hoy</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {gateStats?.livesToday || 0}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center">
                <Users className="h-8 w-8 text-purple-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-500">Total Lives</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {gateStats?.totalLives?.toLocaleString() || '0'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;