import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';
import AnimatedForm from '../components/AnimatedForm';
import AnimatedInput from '../components/AnimatedInput';
import AnimatedButton from '../components/AnimatedButton';
import AnimatedBackground from '../components/AnimatedBackground';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const from = location.state?.from?.pathname || '/';

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      toast.success('¡Inicio de sesión exitoso!');
      navigate(from, { replace: true });
    } else {
      toast.error(result.error);
    }
    
    setLoading(false);
  };

  return (
    <>
      <AnimatedBackground />
      <AnimatedForm
        title="Iniciar Sesión"
        subtitle="Accede a tu cuenta para continuar"
        linkText="¿No tienes cuenta? Crear una nueva"
        linkTo="/register"
      >
        <form onSubmit={handleSubmit} className="space-y-6">
          <AnimatedInput
            type="email"
            label="Email"
            placeholder="tu@email.com"
            value={formData.email}
            onChange={handleChange}
            required
            icon={Mail}
            name="email"
            autoComplete="email"
          />
          
          <AnimatedInput
            type="password"
            label="Contraseña"
            placeholder="Tu contraseña"
            value={formData.password}
            onChange={handleChange}
            required
            icon={Lock}
            name="password"
            autoComplete="current-password"
            showPassword={showPassword}
            onTogglePassword={() => setShowPassword(!showPassword)}
          />

          <AnimatedButton
            type="submit"
            disabled={loading}
            loading={loading}
            className="w-full"
            size="lg"
          >
            {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </AnimatedButton>
        </form>
      </AnimatedForm>
    </>
  );
};

export default Login;
