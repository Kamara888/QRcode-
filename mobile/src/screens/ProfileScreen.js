import React, {useState, useEffect} from 'react';
import {
  View, Text, TextInput, StyleSheet, Alert, ScrollView,
  TouchableOpacity,
} from 'react-native';
import {authAPI} from '../services/api';
import {getUser, logout} from '../utils/storage';
import LoadingButton from '../components/LoadingButton';

const ProfileScreen = ({navigation}) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    first_name: '', last_name: '', email: '', phone: '',
  });

  useEffect(() => {
    (async () => {
      const u = await getUser();
      setUser(u);
      if (u) {
        setForm({
          first_name: u.first_name || '',
          last_name: u.last_name || '',
          email: u.email || '',
          phone: u.phone || '',
        });
      }
    })();
  }, []);

  const handleUpdate = async () => {
    setLoading(true);
    try {
      const res = await authAPI.updateProfile(form);
      setUser(res.data);
      Alert.alert('Success', 'Profile updated');
    } catch (e) {
      Alert.alert('Error', 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigation.reset({index: 0, routes: [{name: 'Login'}]});
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {user?.first_name?.[0]}{user?.last_name?.[0] || user?.username?.[0]}
          </Text>
        </View>
        <Text style={styles.name}>
          {user?.first_name} {user?.last_name}
        </Text>
        <Text style={styles.username}>@{user?.username}</Text>
        <View style={styles.roleBadge}>
          <Text style={styles.roleText}>{user?.role?.toUpperCase()}</Text>
        </View>
      </View>
      <View style={styles.form}>
        <Text style={styles.sectionTitle}>Edit Profile</Text>
        <TextInput
          style={styles.input} placeholder="First Name"
          value={form.first_name} onChangeText={v => setForm(p => ({...p, first_name: v}))}
        />
        <TextInput
          style={styles.input} placeholder="Last Name"
          value={form.last_name} onChangeText={v => setForm(p => ({...p, last_name: v}))}
        />
        <TextInput
          style={styles.input} placeholder="Email"
          value={form.email} onChangeText={v => setForm(p => ({...p, email: v}))}
          keyboardType="email-address"
        />
        <TextInput
          style={styles.input} placeholder="Phone"
          value={form.phone} onChangeText={v => setForm(p => ({...p, phone: v}))}
          keyboardType="phone-pad"
        />
        <LoadingButton title="Update Profile" onPress={handleUpdate} loading={loading} />
        <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f0f4ff'},
  header: {alignItems: 'center', paddingVertical: 30, backgroundColor: '#fff'},
  avatar: {
    width: 80, height: 80, borderRadius: 40,
    backgroundColor: '#2563eb', justifyContent: 'center', alignItems: 'center',
    marginBottom: 10,
  },
  avatarText: {fontSize: 32, color: '#fff', fontWeight: 'bold'},
  name: {fontSize: 20, fontWeight: 'bold', color: '#1e3a5f'},
  username: {fontSize: 14, color: '#64748b', marginTop: 2},
  roleBadge: {
    backgroundColor: '#dbeafe', paddingHorizontal: 16, paddingVertical: 4,
    borderRadius: 12, marginTop: 8,
  },
  roleText: {color: '#2563eb', fontSize: 12, fontWeight: '600'},
  form: {padding: 20},
  sectionTitle: {fontSize: 18, fontWeight: '600', color: '#1e3a5f', marginBottom: 15},
  input: {
    backgroundColor: '#fff', padding: 14, borderRadius: 10,
    marginBottom: 12, borderWidth: 1, borderColor: '#e2e8f0', fontSize: 16,
  },
  logoutBtn: {
    backgroundColor: '#fee2e2', padding: 15, borderRadius: 10,
    alignItems: 'center', marginTop: 20,
  },
  logoutText: {color: '#dc2626', fontSize: 16, fontWeight: '600'},
});

export default ProfileScreen;
