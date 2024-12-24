import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  config: {
    initialColorMode: 'light',
    useSystemColorMode: true,
  },
  colors: {
    brand: {
      50: '#e3f2fd',
      100: '#bbdefb',
      200: '#90caf9',
      300: '#64b5f6',
      400: '#42a5f5',
      500: '#2196f3',
      600: '#1e88e5',
      700: '#1976d2',
      800: '#1565c0',
      900: '#0d47a1',
    },
  },
  fonts: {
    heading: '"Inter", sans-serif',
    body: '"Inter", sans-serif',
  },
  styles: {
    global: (props) => ({
      body: {
        bg: props.colorMode === 'dark' ? 'gray.800' : 'white',
        color: props.colorMode === 'dark' ? 'white' : 'gray.800',
      },
    }),
  },
  components: {
    Button: {
      defaultProps: {
        colorScheme: 'brand',
      },
    },
    Card: {
      baseStyle: (props) => ({
        container: {
          bg: props.colorMode === 'dark' ? 'gray.700' : 'white',
          color: props.colorMode === 'dark' ? 'white' : 'inherit',
        },
      }),
    },
    Table: {
      variants: {
        simple: (props) => ({
          th: {
            bg: props.colorMode === 'dark' ? 'gray.700' : 'gray.50',
            color: props.colorMode === 'dark' ? 'white' : 'gray.600',
          },
          td: {
            bg: props.colorMode === 'dark' ? 'gray.800' : 'white',
            color: props.colorMode === 'dark' ? 'white' : 'inherit',
          },
        }),
      },
    },
  },
});

export default theme;
