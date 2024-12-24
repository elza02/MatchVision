import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Container } from '@chakra-ui/react';
import Navbar from './Navbar';

function Layout() {
  return (
    <Box minH="100vh" bg="gray.50">
      <Navbar />
      <Container maxW="container.xl" py={8}>
        <Outlet />
      </Container>
    </Box>
  );
}

export default Layout;
