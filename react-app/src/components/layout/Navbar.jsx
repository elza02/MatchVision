import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Flex,
  HStack,
  Link,
  IconButton,
  Button,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useDisclosure,
  useColorMode,
  useColorModeValue,
  Image,
  Text,
} from '@chakra-ui/react';
import { HamburgerIcon, CloseIcon, MoonIcon, SunIcon } from '@chakra-ui/icons';
import { FaFutbol, FaUsers, FaTrophy, FaChartBar } from 'react-icons/fa';
import logo from '../../assets/logo.svg';

const Links = [
  { name: 'Matches', to: '/matches', icon: FaFutbol },
  { name: 'Teams', to: '/teams', icon: FaUsers },
  { name: 'Standings', to: '/standings', icon: FaTrophy },
  { name: 'Analytics', to: '/analytics', icon: FaChartBar },
];

const Navbar = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { colorMode, toggleColorMode } = useColorMode();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box bg={bgColor} px={4} borderBottom="1px" borderColor={borderColor}>
      <Flex h={16} alignItems="center" justifyContent="space-between">
        <IconButton
          size="md"
          icon={isOpen ? <CloseIcon /> : <HamburgerIcon />}
          aria-label="Open Menu"
          display={{ md: 'none' }}
          onClick={isOpen ? onClose : onOpen}
        />
        
        <HStack spacing={8} alignItems="center">
          <Box>
            <RouterLink to="/">
              <Flex align="center" gap={2}>
                <Image src={logo} alt="Logo" boxSize="40px" />
                <Text fontSize="lg" fontWeight="bold" display={{ base: 'none', md: 'block' }}>
                  Football Analytics
                </Text>
              </Flex>
            </RouterLink>
          </Box>
          <HStack as="nav" spacing={4} display={{ base: 'none', md: 'flex' }}>
            {Links.map((link) => (
              <Link
                key={link.name}
                as={RouterLink}
                to={link.to}
                px={2}
                py={1}
                rounded="md"
                _hover={{
                  textDecoration: 'none',
                  bg: useColorModeValue('gray.200', 'gray.700'),
                }}
              >
                <Flex align="center" gap={2}>
                  <link.icon />
                  {link.name}
                </Flex>
              </Link>
            ))}
          </HStack>
        </HStack>

        <Flex alignItems="center">
          <IconButton
            aria-label="Toggle Dark Mode"
            icon={colorMode === 'dark' ? <SunIcon /> : <MoonIcon />}
            onClick={toggleColorMode}
            variant="ghost"
            mr={2}
          />
          
          <Menu>
            <MenuButton
              as={Button}
              variant="ghost"
              size="sm"
              display={{ base: 'block', md: 'none' }}
            >
              Menu
            </MenuButton>
            <MenuList>
              {Links.map((link) => (
                <MenuItem key={link.name} as={RouterLink} to={link.to}>
                  <Flex align="center" gap={2}>
                    <link.icon />
                    {link.name}
                  </Flex>
                </MenuItem>
              ))}
            </MenuList>
          </Menu>
        </Flex>
      </Flex>
    </Box>
  );
};

export default Navbar;
