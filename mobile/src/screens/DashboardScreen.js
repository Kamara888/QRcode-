import React, {useState, useCallback} from 'react';
import {
  View, Text, StyleSheet, ScrollView, RefreshControl,
  ActivityIndicator,
} from 'react-native';
import {useFocusEffect} from '@react-navigation/native';
import {attendanceAPI, coursesAPI} from '../services/api';

const DashboardScreen = () => {
  const [courses, setCourses] = useState([]);
  const [summary, setSummary] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const [coursesRes, summaryRes] = await Promise.all([
        coursesAPI.myCourses(),
        attendanceAPI.summary(),
      ]);
      setCourses(coursesRes.data);
      setSummary(summaryRes.data);
    } catch (e) {
      console.log(e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, []),
  );

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  const getColor = pct => {
    if (pct >= 75) return '#22c55e';
    if (pct >= 50) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.greeting}>My Courses</Text>
      {courses.length === 0 && (
        <Text style={styles.empty}>No courses enrolled</Text>
      )}
      {courses.map(course => {
        const s = summary.find(s => s.course_id === course.id);
        return (
          <View key={course.id} style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.courseCode}>{course.code}</Text>
              <Text style={[styles.percentage, {color: getColor(s?.percentage || 0)}]}>
                {s ? `${s.percentage}%` : 'N/A'}
              </Text>
            </View>
            <Text style={styles.courseName}>{course.name}</Text>
            <Text style={styles.lecturer}>
              Lecturer: {course.lecturer_name || 'TBA'}
            </Text>
            {s && (
              <View style={styles.statsRow}>
                <View style={styles.stat}>
                  <Text style={styles.statValue}>{s.attended}</Text>
                  <Text style={styles.statLabel}>Present</Text>
                </View>
                <View style={styles.stat}>
                  <Text style={[styles.statValue, {color: '#f59e0b'}]}>{s.late}</Text>
                  <Text style={styles.statLabel}>Late</Text>
                </View>
                <View style={styles.stat}>
                  <Text style={[styles.statValue, {color: '#ef4444'}]}>{s.absent}</Text>
                  <Text style={styles.statLabel}>Absent</Text>
                </View>
                <View style={styles.stat}>
                  <Text style={styles.statValue}>{s.total_classes}</Text>
                  <Text style={styles.statLabel}>Total</Text>
                </View>
              </View>
            )}
          </View>
        );
      })}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f0f4ff', padding: 15},
  center: {flex: 1, justifyContent: 'center', alignItems: 'center'},
  greeting: {fontSize: 22, fontWeight: 'bold', color: '#1e3a5f', marginBottom: 15},
  empty: {textAlign: 'center', color: '#64748b', marginTop: 40, fontSize: 16},
  card: {
    backgroundColor: '#fff', borderRadius: 12, padding: 16,
    marginBottom: 12, elevation: 2, shadowColor: '#000',
    shadowOffset: {width: 0, height: 1}, shadowOpacity: 0.1, shadowRadius: 3,
  },
  cardHeader: {flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center'},
  courseCode: {fontSize: 18, fontWeight: 'bold', color: '#2563eb'},
  percentage: {fontSize: 22, fontWeight: 'bold'},
  courseName: {fontSize: 14, color: '#475569', marginTop: 4},
  lecturer: {fontSize: 12, color: '#94a3b8', marginTop: 4},
  statsRow: {flexDirection: 'row', justifyContent: 'space-around', marginTop: 12, paddingTop: 12, borderTopWidth: 1, borderTopColor: '#f1f5f9'},
  stat: {alignItems: 'center'},
  statValue: {fontSize: 18, fontWeight: 'bold', color: '#1e3a5f'},
  statLabel: {fontSize: 11, color: '#94a3b8', marginTop: 2},
});

export default DashboardScreen;
