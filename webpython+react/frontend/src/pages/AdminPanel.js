import React, { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';
import { 
  Users, 
  Key, 
  Settings, 
  BarChart3,
  Trash2,
  Plus,
  Shield,
  UserCheck,
  UserX
} from 'lucide-react';
import toast from 'react-hot-toast';

const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('stats');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [keys, setKeys] = useState([]);
  const [gateways, setGateways] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newKey, setNewKey] = useState('');
  const [newKeyDays, setNewKeyDays] = useState(30);
  const [extendDays, setExtendDays] = useState(30);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, usersRes, keysRes, gatewaysRes] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.getUsers(),
        adminAPI.getKeys(),
        adminAPI.getGateways()
      ]);
      
      setStats(statsRes.data);
      setUsers(usersRes.data);
      setKeys(keysRes.data);
      setGateways(gatewaysRes.data);
    } catch (error) {
      toast.error('Error al cargar los datos');
    } finally {
      setLoading(false);
    }
  };

  const toggleUserStatus = async (userId) => {
    try {
      await adminAPI.toggleUserStatus(userId);
      toast.success('Estado del usuario actualizado');
      fetchData();
    } catch (error) {
      toast.error('Error al actualizar el usuario');
    }
  };

  const toggleUserAdmin = async (userId) => {
    try {
      await adminAPI.toggleUserAdmin(userId);
      toast.success('Permisos de admin actualizados');
      fetchData();
    } catch (error) {
      toast.error('Error al actualizar los permisos');
    }
  };

  const createKey = async () => {
    if (!newKey.trim()) {
      toast.error('La key no puede estar vacía');
      return;
    }

    try {
      await adminAPI.createKey({ key: newKey, duration_days: Number(newKeyDays) || 30 });
      toast.success('Key creada exitosamente');
      setNewKey('');
      setNewKeyDays(30);
      fetchData();
    } catch (error) {
      toast.error('Error al crear la key');
    }
  };

  const toggleKeyStatus = async (keyId) => {
    try {
      await adminAPI.toggleKeyStatus(keyId);
      toast.success('Estado de la key actualizado');
      fetchData();
    } catch (error) {
      toast.error('Error al actualizar la key');
    }
  };

  const deleteKey = async (keyId) => {
    if (!window.confirm('¿Estás seguro de que quieres eliminar esta key?')) {
      return;
    }

    try {
      await adminAPI.deleteKey(keyId);
      toast.success('Key eliminada exitosamente');
      fetchData();
    } catch (error) {
      toast.error('Error al eliminar la key');
    }
  };

  const renewKey = async (keyId) => {
    try {
      await adminAPI.renewKey(keyId);
      toast.success('Suscripción renovada con la key');
      fetchData();
    } catch (error) {
      toast.error('Error al renovar con la key');
    }
  };

  const extendUser = async (userId) => {
    try {
      await adminAPI.extendUser(userId, Number(extendDays) || 30);
      toast.success('Suscripción extendida');
      fetchData();
    } catch (error) {
      toast.error('Error al extender suscripción');
    }
  };

  const tabs = [
    { id: 'stats', name: 'Estadísticas', icon: BarChart3 },
    { id: 'users', name: 'Usuarios', icon: Users },
    { id: 'keys', name: 'Keys', icon: Key },
    { id: 'gateways', name: 'Gateways', icon: Settings },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Panel de Administración</h1>
        <p className="text-gray-600">
          Gestiona usuarios, keys y configuraciones del sistema
        </p>
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
      {activeTab === 'stats' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="card">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Usuarios</p>
                <p className="text-2xl font-semibold text-gray-900">{stats?.total_users}</p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <UserCheck className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Usuarios Activos</p>
                <p className="text-2xl font-semibold text-gray-900">{stats?.active_users}</p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <Key className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Keys Activas</p>
                <p className="text-2xl font-semibold text-gray-900">{stats?.active_keys}</p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <Settings className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Gateways</p>
                <p className="text-2xl font-semibold text-gray-900">{stats?.total_gateways}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'users' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Usuarios</h2>
          <div className="flex items-center space-x-3 mb-4">
            <label className="text-sm text-gray-600">Extender días:</label>
            <input type="number" min="1" value={extendDays} onChange={(e)=>setExtendDays(e.target.value)} className="input-field w-24" />
            <span className="text-xs text-gray-500">Aplicar en botón de cada usuario</span>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Usuario
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Telegram ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Admin
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Expira
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {user.username}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.telegram_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => toggleUserStatus(user.id)}
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          user.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {user.is_active ? (
                          <>
                            <UserCheck className="h-3 w-3 mr-1" />
                            Activo
                          </>
                        ) : (
                          <>
                            <UserX className="h-3 w-3 mr-1" />
                            Inactivo
                          </>
                        )}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {user.is_admin && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          <Shield className="h-3 w-3 mr-1" />
                          Admin
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.subscription_expires_at ? new Date(user.subscription_expires_at).toLocaleString() : '—'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => toggleUserAdmin(user.id)}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        {user.is_admin ? 'Quitar Admin' : 'Hacer Admin'}
                      </button>
                      <button
                        onClick={() => extendUser(user.id)}
                        className="ml-3 text-green-600 hover:text-green-900"
                      >
                        Extender
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'keys' && (
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Keys de Registro</h2>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newKey}
                onChange={(e) => setNewKey(e.target.value)}
                placeholder="Nueva key"
                className="input-field"
              />
              <input
                type="number"
                value={newKeyDays}
                min={1}
                onChange={(e) => setNewKeyDays(e.target.value)}
                placeholder="Días"
                className="input-field w-24"
              />
              <button onClick={createKey} className="btn-primary">
                <Plus className="h-4 w-4 mr-1" />
                Crear
              </button>
            </div>
          </div>
          
          <div className="space-y-3">
            {keys.map((key) => (
              <div
                key={key.id}
                className="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                    {key.key}
                  </code>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    key.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {key.is_active ? 'Activa' : 'Inactiva'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {key.duration_days} días
                  </span>
                  {key.expires_at && (
                    <span className="text-xs text-gray-500">
                      expira: {new Date(key.expires_at).toLocaleString()}
                    </span>
                  )}
                  {key.activated_at && (
                    <span className="text-xs text-gray-500">
                      activada: {new Date(key.activated_at).toLocaleString()}
                    </span>
                  )}
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => toggleKeyStatus(key.id)}
                    className="text-sm text-primary-600 hover:text-primary-900"
                  >
                    {key.is_active ? 'Desactivar' : 'Activar'}
                  </button>
                  {key.user_id && (
                    <button
                      onClick={() => renewKey(key.id)}
                      className="text-sm text-green-600 hover:text-green-900"
                    >
                      Renovar
                    </button>
                  )}
                  <button
                    onClick={() => deleteKey(key.id)}
                    className="text-sm text-red-600 hover:text-red-900"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'gateways' && (
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Gateways</h2>
            <button className="btn-primary">
              <Plus className="h-4 w-4 mr-1" />
              Nuevo Gateway
            </button>
          </div>
          
          <div className="text-center py-8">
            <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              Los gateways se configurarán cuando los proporciones
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;
