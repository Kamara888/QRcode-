import React from 'react';
import {TouchableOpacity, Text, ActivityIndicator, StyleSheet} from 'react-native';

const LoadingButton = ({title, onPress, loading, style, textStyle}) => (
  <TouchableOpacity
    style={[styles.button, style]}
    onPress={onPress}
    disabled={loading}>
    {loading ? (
      <ActivityIndicator color="#fff" />
    ) : (
      <Text style={[styles.text, textStyle]}>{title}</Text>
    )}
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#2563eb',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginVertical: 5,
  },
  text: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default LoadingButton;
