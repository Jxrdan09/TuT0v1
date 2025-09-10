import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Mail, User, Hash, Key, Lock, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';
import AnimatedForm from '../components/AnimatedForm';
import AnimatedInput from '../components/AnimatedInput';
import AnimatedButton from '../components/AnimatedButton';
import AnimatedBackground from '../components/AnimatedBackground';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    telegram_id: '',
    key: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      toast.error('Las contraseñas no coinciden');
      return;
    }
    
    if (formData.password.length < 6) {
      toast.error('La contraseña debe tener al menos 6 caracteres');
      return;
    }
    
    if (!formData.telegram_id.match(/^\d+$/)) {
      toast.error('El ID de Telegram debe ser numérico');
      return;
    }
    
    setLoading(true);

    const { confirmPassword, ...registerData } = formData;
    const result = await register(registerData);
    
    if (result.success) {
      toast.success('¡Registro exitoso! Ahora puedes iniciar sesión.');
      navigate('/login');
    } else {
      toast.error(result.error);
    }
    
    setLoading(false);
  };

  return (
    <>
      <AnimatedBackground />
      <AnimatedForm
        title="Crear Cuenta"
        subtitle="Únete a nuestra plataforma de scripts"
        linkText="¿Ya tienes cuenta? Iniciar sesión"
        linkTo="/login"
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
            type="text"
            label="Nombre de Usuario"
            placeholder="tu_usuario"
            value={formData.username}
            onChange={handleChange}
            required
            icon={User}
            name="username"
            autoComplete="username"
          />
          
          <AnimatedInput
            type="text"
            label="ID de Telegram"
            placeholder="123456789"
            value={formData.telegram_id}
            onChange={handleChange}
            required
            icon={Hash}
            name="telegram_id"
          />
          
          <AnimatedInput
            type="text"
            label="Key de Registro"
            placeholder="tu-key-de-registro"
            value={formData.key}
            onChange={handleChange}
            required
            icon={Key}
            name="key"
          />
          
          <AnimatedInput
            type="password"
            label="Contraseña"
            placeholder="Mínimo 6 caracteres"
            value={formData.password}
            onChange={handleChange}
            required
            icon={Lock}
            name="password"
            autoComplete="new-password"
            showPassword={showPassword}
            onTogglePassword={() => setShowPassword(!showPassword)}
          />
          
          <AnimatedInput
            type="password"
            label="Confirmar Contraseña"
            placeholder="Repite tu contraseña"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
            icon={Lock}
            name="confirmPassword"
            autoComplete="new-password"
            showPassword={showConfirmPassword}
            onTogglePassword={() => setShowConfirmPassword(!showConfirmPassword)}
          />

          <AnimatedButton
            type="submit"
            disabled={loading}
            loading={loading}
            className="w-full"
            size="lg"
          >
            {loading ? 'Creando cuenta...' : 'Crear Cuenta'}
          </AnimatedButton>
        </form>
      </AnimatedForm>
    </>
  );
};

export default Register;
