# OBIS Reader Library

A standalone Python library for reading and parsing OBIS (Object Identification System) codes from smart meters according to IEC 62056-21 standard. This library provides clean, object-oriented interfaces for smart meter communication without external framework dependencies.

## Overview

The OBIS Reader library provides functionality to:
- Parse OBIS codes into their components
- Validate OBIS code formats
- Read data from smart meters
- Support multiple meter types (electricity, gas, water, heat, cooling)
- Transform and validate meter data

## Features

- **Standalone Implementation**: No external framework dependencies
- **OBIS Code Parsing**: Parse OBIS codes according to IEC 62056-21 standard
- **Multiple Meter Types**: Support for electricity, gas, water, heat, and cooling meters
- **Data Validation**: Comprehensive data validation and transformation
- **Built-in Logging**: Simple logging system with configurable levels
- **Statistics Tracking**: Detailed performance and usage statistics
- **Sample Data**: Built-in sample data generation for testing
- **Extensible**: Easy to extend for custom meter types and OBIS codes

## Installation

### Prerequisites

No external dependencies required! The library is completely standalone.

### Usage

Simply copy the `obis.py` file into your project and import it:

```python
from obis import OBISReader, OBISCode, OBISCodeType, MeterData
```

## Quick Start

```python
from obis import OBISReader, OBISCode

# Create OBIS reader
reader = OBISReader(
    device_id="meter_001",
    meter_type="electricity",
    timeout=5.0,
    retry_count=3
)

# Add OBIS codes
voltage_code = OBISCode(
    code="1.0.32.7.0.255",
    name="l1_voltage",
    description="L1 Voltage",
    unit="V",
    data_type="float"
)
reader.add_obis_code(voltage_code)

# Read data
data = reader.read_data()
print(data)
```

## OBIS Code Format

OBIS codes follow the format: `A.B.C.D.E.F`

- **A**: Media (1=electricity, 2=gas, 3=water, 4=heat, 5=cooling)
- **B**: Channel
- **C**: Measurement
- **D**: Measurement type
- **E**: Tariff
- **F**: Storage

### Example OBIS Codes

#### Electricity Meters
- `1.0.0.0.0.255` - Meter ID
- `1.0.1.7.0.255` - Current Power (W)
- `1.0.1.8.0.255` - Total Energy (kWh)
- `1.0.32.7.0.255` - L1 Voltage (V)
- `1.0.31.7.0.255` - L1 Current (A)

#### Gas Meters
- `7.0.0.0.0.255` - Meter ID
- `7.0.1.7.0.255` - Current Flow (m³/h)
- `7.0.1.8.0.255` - Total Volume (m³)

#### Water Meters
- `8.0.0.0.0.255` - Meter ID
- `8.0.1.7.0.255` - Current Flow (m³/h)
- `8.0.1.8.0.255` - Total Volume (m³)

## Supported Meter Types

### Electricity Meters
- Power measurements (W, kW)
- Energy consumption (kWh)
- Voltage measurements (V)
- Current measurements (A)
- Power factor
- Frequency

### Gas Meters
- Flow rate (m³/h)
- Volume consumption (m³)
- Temperature compensation
- Pressure measurements

### Water Meters
- Flow rate (m³/h)
- Volume consumption (m³)
- Temperature measurements
- Quality parameters

### Heat Meters
- Heat energy (kWh)
- Temperature differences
- Flow measurements

### Cooling Meters
- Cooling energy (kWh)
- Temperature measurements
- Flow rate

## Configuration

### Logging

The library uses a simple logging system that can be customized:

```python
from obis import SimpleLogger

# Create custom logger
logger = SimpleLogger(log_level=1)  # 0=info, 1=warning, 2=error

# Use with OBIS reader
reader = OBISReader(device_id="test", logger=logger)
```

### Health Monitoring

Health monitoring is automatically enabled:

```python
# Check health status
status = reader.get_status()
print(f"Health: {status['health_status']}")
print(f"Last check: {status['last_health_check']}")
```

### Statistics

The library provides detailed statistics:

```python
# Get statistics
stats = reader.get_status()['stats']
print(f"Total reads: {stats['total_reads']}")
print(f"Successful reads: {stats['successful_reads']}")
print(f"Failed reads: {stats['failed_reads']}")
print(f"Validation errors: {stats['validation_errors']}")
```

## Examples

### Complete Electricity Meter Example

```python
from obis import OBISReader, OBISCode

# Create reader
reader = OBISReader("electricity_meter", "electricity")

# Add common electricity codes
codes = [
    OBISCode("1.0.0.0.0.255", "meter_id", "Meter ID", "", "string"),
    OBISCode("1.0.1.7.0.255", "current_power", "Current Power", "W", "float"),
    OBISCode("1.0.1.8.0.255", "total_energy", "Total Energy", "kWh", "float"),
    OBISCode("1.0.21.7.0.255", "l1_power", "L1 Power", "W", "float"),
    OBISCode("1.0.22.7.0.255", "l2_power", "L2 Power", "W", "float"),
    OBISCode("1.0.23.7.0.255", "l3_power", "L3 Power", "W", "float"),
    OBISCode("1.0.32.7.0.255", "l1_voltage", "L1 Voltage", "V", "float"),
    OBISCode("1.0.52.7.0.255", "l2_voltage", "L2 Voltage", "V", "float"),
    OBISCode("1.0.72.7.0.255", "l3_voltage", "L3 Voltage", "V", "float"),
    OBISCode("1.0.31.7.0.255", "l1_current", "L1 Current", "A", "float"),
    OBISCode("1.0.51.7.0.255", "l2_current", "L2 Current", "A", "float"),
    OBISCode("1.0.71.7.0.255", "l3_current", "L3 Current", "A", "float")
]

for code in codes:
    reader.add_obis_code(code)

# Read and save data
data = reader.read_data()
reader.save_data(data)

# Get status
status = reader.get_status()
print(f"Health: {status['health_status']}")
print(f"Statistics: {status['stats']}")
```

### Gas Meter Example

```python
from obis import OBISReader, OBISCode

# Create gas meter reader
reader = OBISReader("gas_meter", "gas")

# Add gas meter codes
codes = [
    OBISCode("7.0.0.0.0.255", "meter_id", "Meter ID", "", "string"),
    OBISCode("7.0.1.7.0.255", "current_flow", "Current Flow", "m³/h", "float"),
    OBISCode("7.0.1.8.0.255", "total_volume", "Total Volume", "m³", "float"),
    OBISCode("7.0.2.7.0.255", "temperature", "Temperature", "°C", "float"),
    OBISCode("7.0.3.7.0.255", "pressure", "Pressure", "bar", "float")
]

for code in codes:
    reader.add_obis_code(code)

# Read data
data = reader.read_data()
print("Gas Meter Data:", data)
```

### Water Meter Example

```python
from obis import OBISReader, OBISCode

# Create water meter reader
reader = OBISReader("water_meter", "water")

# Add water meter codes
codes = [
    OBISCode("8.0.0.0.0.255", "meter_id", "Meter ID", "", "string"),
    OBISCode("8.0.1.7.0.255", "current_flow", "Current Flow", "m³/h", "float"),
    OBISCode("8.0.1.8.0.255", "total_volume", "Total Volume", "m³", "float"),
    OBISCode("8.0.2.7.0.255", "temperature", "Temperature", "°C", "float")
]

for code in codes:
    reader.add_obis_code(code)

# Read data
data = reader.read_data()
print("Water Meter Data:", data)
```

### Custom OBIS Code Validation

```python
from obis import OBISCodeParser, OBISCodeType

# Create parser
parser = OBISCodeParser()

# Parse OBIS code
obis_code = "1.0.32.7.0.255"
parsed = parser.parse_obis_code(obis_code)
print(f"Media: {parsed['media']}")
print(f"Channel: {parsed['channel']}")
print(f"Measurement: {parsed['measurement']}")

# Get code type
code_type = parser.get_code_type(parsed)
print(f"Code type: {code_type.value}")

# Validate code
is_valid = parser.is_valid_code(obis_code)
print(f"Valid: {is_valid}")
```

### Real-time Monitoring Example

```python
from obis import OBISReader, OBISCode
import time

# Create reader
reader = OBISReader("smart_meter", "electricity")

# Add monitoring codes
monitoring_codes = [
    OBISCode("1.0.1.7.0.255", "current_power", "Current Power", "W", "float"),
    OBISCode("1.0.32.7.0.255", "l1_voltage", "L1 Voltage", "V", "float"),
    OBISCode("1.0.31.7.0.255", "l1_current", "L1 Current", "A", "float")
]

for code in monitoring_codes:
    reader.add_obis_code(code)

# Continuous monitoring
while True:
    try:
        data = reader.read_data()
        
        if data:
            print(f"Current Power: {data.get('1.0.1.7.0.255', {}).get('value', 0):.2f} W")
            print(f"L1 Voltage: {data.get('1.0.32.7.0.255', {}).get('value', 0):.1f} V")
            print(f"L1 Current: {data.get('1.0.31.7.0.255', {}).get('value', 0):.2f} A")
            print("-" * 40)
        
        time.sleep(5)  # Read every 5 seconds
        
    except KeyboardInterrupt:
        print("Monitoring stopped by user")
        break
```

## Data Validation

The library includes comprehensive data validation:

### OBIS Code Validation
- Format validation (A.B.C.D.E.F)
- Media type validation
- Component range validation

### Data Type Validation
- Float values for measurements
- Integer values for counters
- String values for identifiers
- Boolean values for status

### Range Validation
- Voltage: 0-500V
- Current: 0-1000A
- Power: 0-100000W
- Energy: 0-999999999kWh
- Flow: 0-1000m³/h
- Volume: 0-999999999m³

## Error Handling

The library includes comprehensive error handling:

- **OBIS Code Errors**: Invalid format or range validation
- **Data Validation Errors**: Type and range validation failures
- **Connection Errors**: Communication failures with meters
- **Logging**: Detailed error logging with different levels

## Performance Considerations

- **Validation**: Validate OBIS codes before adding them
- **Data Types**: Use appropriate data types for your meter
- **Monitoring**: Monitor validation errors in statistics
- **Caching**: Consider caching frequently accessed data

## Troubleshooting

### Common Issues

1. **Invalid OBIS Codes**
   - Verify OBIS code format (A.B.C.D.E.F)
   - Check media type (1-5)
   - Validate component ranges

2. **Data Validation Errors**
   - Check data types (float, int, string, boolean)
   - Verify value ranges
   - Review scale factors

3. **Performance Issues**
   - Monitor validation errors
   - Check for invalid OBIS codes
   - Review logging levels

### Debug Mode

Enable debug logging by setting log level to 0:

```python
logger = SimpleLogger(log_level=0)
```

### OBIS Code Testing

```python
from obis import OBISCodeParser

parser = OBISCodeParser()

# Test various OBIS codes
test_codes = [
    "1.0.0.0.0.255",  # Valid electricity meter ID
    "7.0.1.7.0.255",  # Valid gas meter flow
    "8.0.1.8.0.255",  # Valid water meter volume
    "invalid.code",   # Invalid format
    "1.0.0.0.0",      # Missing component
]

for code in test_codes:
    is_valid = parser.is_valid_code(code)
    print(f"{code}: {'Valid' if is_valid else 'Invalid'}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the examples
3. Create an issue with detailed information

## Version History

- **v1.0.0**: Initial release with OBIS support
- Standalone implementation without external framework dependencies
- Comprehensive OBIS code parsing and validation
- Support for multiple meter types
- Built-in data validation and transformation
- Sample data generation for testing

## References

- IEC 62056-21: Electricity metering - Data exchange for meter reading, tariff and load control - Part 21: Direct local data exchange
- OBIS (Object Identification System) standard
- Smart meter communication protocols 
