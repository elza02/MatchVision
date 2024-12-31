import { extendTheme } from '@chakra-ui/react';

const config = {
  initialColorMode: 'dark',
  useSystemColorMode: false,
};

const theme = extendTheme({
  config,
  semanticTokens: {
    colors: {
      'chakra-body-bg': { _light: 'white', _dark: 'gray.800' },
      'chakra-body-text': { _light: 'gray.800', _dark: 'whiteAlpha.900' },
    },
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
        color: props.colorMode === 'dark' ? 'whiteAlpha.900' : 'gray.800',
        lineHeight: 'base',
      },
    }),
  },
  components: {
    Button: {
      defaultProps: {
        colorScheme: 'brand',
      },
      variants: {
        solid: (props) => ({
          bg: props.colorMode === 'dark' ? 'brand.500' : 'brand.500',
          color: 'white',
          _hover: {
            bg: props.colorMode === 'dark' ? 'brand.600' : 'brand.600',
          },
        }),
        ghost: (props) => ({
          color: props.colorMode === 'dark' ? 'whiteAlpha.900' : 'gray.800',
          _hover: {
            bg: props.colorMode === 'dark' ? 'whiteAlpha.200' : 'blackAlpha.100',
          },
        }),
      },
    },
    Card: {
      baseStyle: (props) => ({
        container: {
          bg: props.colorMode === 'dark' ? 'gray.700' : 'white',
          color: props.colorMode === 'dark' ? 'whiteAlpha.900' : 'gray.800',
          boxShadow: props.colorMode === 'dark' ? 'lg' : 'md',
          borderRadius: 'lg',
          borderWidth: '1px',
          borderColor: props.colorMode === 'dark' ? 'gray.600' : 'gray.200',
          overflow: 'hidden',
          transition: 'all 0.2s',
          _hover: {
            borderColor: props.colorMode === 'dark' ? 'gray.500' : 'gray.300',
            boxShadow: 'xl',
          },
        },
      }),
    },
    Table: {
      baseStyle: {
        table: {
          borderCollapse: 'separate',
          borderSpacing: 0,
        },
      },
      variants: {
        simple: (props) => ({
          th: {
            bg: props.colorMode === 'dark' ? 'gray.700' : 'gray.50',
            color: props.colorMode === 'dark' ? 'whiteAlpha.900' : 'gray.800',
            borderBottom: '2px',
            borderColor: props.colorMode === 'dark' ? 'gray.600' : 'gray.200',
            fontSize: 'sm',
            fontWeight: 'semibold',
            padding: '4',
            textTransform: 'uppercase',
            letterSpacing: 'wider',
          },
          td: {
            bg: props.colorMode === 'dark' ? 'gray.800' : 'white',
            color: props.colorMode === 'dark' ? 'whiteAlpha.900' : 'gray.800',
            borderBottom: '1px',
            borderColor: props.colorMode === 'dark' ? 'gray.600' : 'gray.200',
            fontSize: 'sm',
            padding: '4',
            transition: 'all 0.2s',
          },
          caption: {
            color: props.colorMode === 'dark' ? 'gray.400' : 'gray.600',
            fontSize: 'sm',
            padding: '2',
          },
          tbody: {
            tr: {
              _hover: {
                bg: props.colorMode === 'dark' ? 'gray.700' : 'gray.50',
              },
            },
          },
        }),
      },
    },
    Input: {
      variants: {
        outline: (props) => ({
          field: {
            bg: props.colorMode === 'dark' ? 'gray.700' : 'white',
            borderColor: props.colorMode === 'dark' ? 'gray.600' : 'gray.300',
            color: props.colorMode === 'dark' ? 'whiteAlpha.900' : 'gray.800',
            borderWidth: '1px',
            _hover: {
              borderColor: props.colorMode === 'dark' ? 'gray.500' : 'gray.400',
            },
            _focus: {
              borderColor: 'brand.500',
              boxShadow: `0 0 0 1px ${props.colorMode === 'dark' ? '#2196f3' : '#2196f3'}`,
            },
          },
        }),
      },
    },
    Select: {
      variants: {
        outline: (props) => ({
          field: {
            bg: props.colorMode === 'dark' ? 'gray.700' : 'white',
            borderColor: props.colorMode === 'dark' ? 'gray.600' : 'gray.300',
            color: props.colorMode === 'dark' ? 'whiteAlpha.900' : 'gray.800',
            borderWidth: '1px',
            _hover: {
              borderColor: props.colorMode === 'dark' ? 'gray.500' : 'gray.400',
            },
            _focus: {
              borderColor: 'brand.500',
              boxShadow: `0 0 0 1px ${props.colorMode === 'dark' ? '#2196f3' : '#2196f3'}`,
            },
          },
        }),
      },
    },
  },
});

export default theme;
