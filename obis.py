import re
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum


class OBISCodeType(Enum):
    """Enumeration for OBIS code types."""
    ELECTRICITY = "electricity"
    GAS = "gas"
    WATER = "water"
    HEAT = "heat"
    COOLING = "cooling"


@dataclass
class OBISCode:
    """Data class for OBIS code configuration."""
    code: str
    name: str
    description: str
    unit: str
    data_type: str = "float"
    scale_factor: float = 1.0
    validation_rules: Optional[Dict[str, Any]] = None


@dataclass
class MeterData:
    """Data class for meter data."""
    meter_id: str
    timestamp: float
    obis_code: str
    value: Any
    unit: str
    quality: str = "good"
    source: str = "obis_reader"


class OBISCodeParser:
    """Parser for OBIS codes according to IEC 62056-21 standard."""
    
    @staticmethod
    def parse_obis_code(code: str) -> Dict[str, Any]:
        """
        Parse an OBIS code into its components.
        
        Args:
            code: OBIS code string (e.g., "1.0.0.0.0.255")
            
        Returns:
            Dictionary with parsed components
        """
        try:
            # Split the code into components
            parts = code.split('.')
            
            if len(parts) != 6:
                raise ValueError(f"Invalid OBIS code format: {code}")
            
            return {
                "media": parts[0],
                "channel": parts[1],
                "measurement": parts[2],
                "measurement_type": parts[3],
                "tariff": parts[4],
                "storage": parts[5],
                "original_code": code
            }
        except Exception as e:
            raise ValueError(f"Failed to parse OBIS code {code}: {str(e)}")
    
    @staticmethod
    def get_code_type(parsed_code: Dict[str, Any]) -> OBISCodeType:
        """
        Determine the type of OBIS code.
        
        Args:
            parsed_code: Parsed OBIS code
            
        Returns:
            OBIS code type
        """
        media = parsed_code.get("media", "")
        
        media_types = {
            "1": OBISCodeType.ELECTRICITY,
            "2": OBISCodeType.GAS,
            "3": OBISCodeType.WATER,
            "4": OBISCodeType.HEAT,
            "5": OBISCodeType.COOLING
        }
        
        return media_types.get(media, OBISCodeType.ELECTRICITY)
    
    @staticmethod
    def is_valid_code(code: str) -> bool:
        """
        Validate OBIS code format.
        
        Args:
            code: OBIS code to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            OBISCodeParser.parse_obis_code(code)
            return True
        except ValueError:
            return False


class SimpleLogger:
    """Simple logger for OBIS reader."""
    
    def __init__(self, log_level: int = 0):
        """
        Initialize logger.
        
        Args:
            log_level: Log level (0=info, 1=warning, 2=error)
        """
        self.log_level = log_level
    
    def log(self, data: Any, log_type: int = 0, visibility: str = "TD", tag: str = "OBISReader") -> None:
        """
        Log a message.
        
        Args:
            data: Data to log
            log_type: Type of log (0=info, 1=warning, 2=error)
            visibility: Visibility level
            tag: Tag for the log
        """
        if log_type >= self.log_level:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            level_str = {0: "INFO", 1: "WARNING", 2: "ERROR"}.get(log_type, "INFO")
            print(f"[{timestamp}] [{level_str}] [{tag}] {data}")


class OBISReader:
    """
    OOP wrapper for OBIS (Object Identification System) reading.
    
    This class provides a clean, object-oriented interface for reading
    and parsing OBIS codes from smart meters with data validation
    and transformation capabilities.
    """
    
    def __init__(
        self,
        device_id: str,
        meter_type: str = "electricity",
        timeout: float = 5.0,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        logger: Optional[SimpleLogger] = None
    ):
        """
        Initialize OBIS Reader.
        
        Args:
            device_id: Unique identifier for the device
            meter_type: Type of meter (electricity, gas, water, etc.)
            timeout: Read timeout in seconds
            retry_count: Number of retry attempts on failure
            retry_delay: Delay between retries in seconds
            logger: Logger instance
        """
        self.device_id = device_id
        self.device_type = "obis_meter"
        self.meter_type = meter_type
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        
        self.logger = logger or SimpleLogger()
        self.parser = OBISCodeParser()
        
        # OBIS code configurations
        self.obis_codes: Dict[str, OBISCode] = {}
        self.code_mappings: Dict[str, str] = {}
        
        # Data validation rules
        self.validation_rules = {
            "electricity": {
                "voltage": {"min": 0, "max": 500, "unit": "V"},
                "current": {"min": 0, "max": 1000, "unit": "A"},
                "power": {"min": 0, "max": 100000, "unit": "W"},
                "energy": {"min": 0, "max": 999999999, "unit": "kWh"}
            },
            "gas": {
                "flow": {"min": 0, "max": 1000, "unit": "m³/h"},
                "volume": {"min": 0, "max": 999999999, "unit": "m³"}
            },
            "water": {
                "flow": {"min": 0, "max": 1000, "unit": "m³/h"},
                "volume": {"min": 0, "max": 999999999, "unit": "m³"}
            }
        }
        
        # Statistics
        self.stats = {
            "total_reads": 0,
            "successful_reads": 0,
            "failed_reads": 0,
            "validation_errors": 0,
            "last_error": None
        }
        
        # Load default OBIS codes
        self._load_default_codes()
    
    def add_obis_code(self, obis_code: OBISCode) -> None:
        """
        Add an OBIS code configuration.
        
        Args:
            obis_code: OBIS code configuration
        """
        if not self.parser.is_valid_code(obis_code.code):
            self.logger.log(
                data=f"Invalid OBIS code format: {obis_code.code}",
                log_type=2,
                visibility="TD",
                tag="OBISReader"
            )
            return
        
        self.obis_codes[obis_code.code] = obis_code
        self.code_mappings[obis_code.name] = obis_code.code
        
        self.logger.log(
            data=f"Added OBIS code: {obis_code.code} ({obis_code.name})",
            log_type=0,
            visibility="TD",
            tag="OBISReader"
        )
    
    def add_obis_codes(self, obis_codes: List[OBISCode]) -> None:
        """
        Add multiple OBIS code configurations.
        
        Args:
            obis_codes: List of OBIS code configurations
        """
        for obis_code in obis_codes:
            self.add_obis_code(obis_code)
    
    def read_obis_data(self, raw_data: str) -> Dict[str, MeterData]:
        """
        Parse OBIS data from raw meter data.
        
        Args:
            raw_data: Raw data string from meter
            
        Returns:
            Dictionary mapping OBIS codes to meter data
        """
        try:
            results = {}
            self.stats["total_reads"] += 1
            
            # Parse the raw data (this is a simplified example)
            # In real implementation, this would parse actual meter protocol data
            parsed_data = self._parse_raw_data(raw_data)
            
            for obis_code, value in parsed_data.items():
                if obis_code in self.obis_codes:
                    # Validate data
                    if self._validate_data(obis_code, value):
                        meter_data = MeterData(
                            meter_id=self.device_id,
                            timestamp=time.time(),
                            obis_code=obis_code,
                            value=value,
                            unit=self.obis_codes[obis_code].unit,
                            quality="good"
                        )
                        results[obis_code] = meter_data
                        self.stats["successful_reads"] += 1
                    else:
                        self.stats["validation_errors"] += 1
                        self.logger.log(
                            data=f"Data validation failed for {obis_code}: {value}",
                            log_type=2,
                            visibility="TD",
                            tag="OBISReader"
                        )
                else:
                    self.logger.log(
                        data=f"Unknown OBIS code: {obis_code}",
                        log_type=1,
                        visibility="TD",
                        tag="OBISReader"
                    )
            
            return results
            
        except Exception as e:
            self.stats["failed_reads"] += 1
            self.stats["last_error"] = str(e)
            
            self.logger.log(
                data=f"Failed to read OBIS data: {str(e)}",
                log_type=2,
                visibility="TD",
                tag="OBISReader"
            )
            return {}
    
    def read_data(self) -> Dict[str, Any]:
        """
        Read data from the device.
        
        Returns:
            Dictionary containing device data
        """
        # This would typically read from the actual meter
        # For demonstration, we'll use sample data
        sample_data = self._get_sample_data()
        meter_data = self.read_obis_data(sample_data)
        
        # Convert to simple dictionary format
        results = {}
        for obis_code, data in meter_data.items():
            results[obis_code] = {
                "value": data.value,
                "unit": data.unit,
                "timestamp": data.timestamp,
                "quality": data.quality
            }
        
        return results
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """
        Save data (placeholder method).
        
        Args:
            data: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This would typically save to the database
            # For now, just log the data
            self.logger.log(
                data=data,
                log_type=0,
                visibility="TD",
                tag="OBISReader"
            )
            return True
        except Exception as e:
            self.logger.log(
                data=f"Failed to save data: {str(e)}",
                log_type=2,
                visibility="TD",
                tag="OBISReader"
            )
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get device status information.
        
        Returns:
            Dictionary containing device status
        """
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "meter_type": self.meter_type,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
            "obis_codes_count": len(self.obis_codes),
            "code_mappings_count": len(self.code_mappings),
            "stats": self.stats.copy()
        }
    
    def _load_default_codes(self) -> None:
        """Load default OBIS codes for the meter type."""
        default_codes = {
            "electricity": [
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
            ],
            "gas": [
                OBISCode("7.0.0.0.0.255", "meter_id", "Meter ID", "", "string"),
                OBISCode("7.0.1.7.0.255", "current_flow", "Current Flow", "m³/h", "float"),
                OBISCode("7.0.1.8.0.255", "total_volume", "Total Volume", "m³", "float")
            ],
            "water": [
                OBISCode("8.0.0.0.0.255", "meter_id", "Meter ID", "", "string"),
                OBISCode("8.0.1.7.0.255", "current_flow", "Current Flow", "m³/h", "float"),
                OBISCode("8.0.1.8.0.255", "total_volume", "Total Volume", "m³", "float")
            ]
        }
        
        codes = default_codes.get(self.meter_type, [])
        for code in codes:
            self.add_obis_code(code)
    
    def _parse_raw_data(self, raw_data: str) -> Dict[str, Any]:
        """
        Parse raw meter data into OBIS code-value pairs.
        
        Args:
            raw_data: Raw data string from meter
            
        Returns:
            Dictionary mapping OBIS codes to values
        """
        # This is a simplified parser
        # In real implementation, this would parse actual meter protocol data
        results = {}
        
        # Example parsing logic (simplified)
        lines = raw_data.strip().split('\n')
        for line in lines:
            if ':' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    obis_code = parts[0].strip()
                    value_str = parts[1].strip()
                    
                    # Try to convert value to appropriate type
                    try:
                        if '.' in value_str:
                            value = float(value_str)
                        else:
                            value = int(value_str)
                        results[obis_code] = value
                    except ValueError:
                        # Keep as string if conversion fails
                        results[obis_code] = value_str
        
        return results
    
    def _validate_data(self, obis_code: str, value: Any) -> bool:
        """
        Validate data according to OBIS code rules.
        
        Args:
            obis_code: OBIS code
            value: Value to validate
            
        Returns:
            True if valid, False otherwise
        """
        if obis_code not in self.obis_codes:
            return False
        
        code_config = self.obis_codes[obis_code]
        
        # Check data type
        if code_config.data_type == "float" and not isinstance(value, (int, float)):
            return False
        elif code_config.data_type == "int" and not isinstance(value, int):
            return False
        elif code_config.data_type == "string" and not isinstance(value, str):
            return False
        
        # Check validation rules
        if code_config.validation_rules:
            rules = code_config.validation_rules
            
            if "min" in rules and value < rules["min"]:
                return False
            if "max" in rules and value > rules["max"]:
                return False
        
        # Check meter type specific rules
        meter_rules = self.validation_rules.get(self.meter_type, {})
        for rule_name, rule_config in meter_rules.items():
            if rule_name in obis_code:
                if "min" in rule_config and value < rule_config["min"]:
                    return False
                if "max" in rule_config and value > rule_config["max"]:
                    return False
        
        return True
    
    def _get_sample_data(self) -> str:
        """
        Get sample data for demonstration purposes.
        
        Returns:
            Sample meter data string
        """
        if self.meter_type == "electricity":
            return """
1.0.0.0.0.255:12345678
1.0.1.7.0.255:2500.5
1.0.1.8.0.255:12345.67
1.0.21.7.0.255:850.2
1.0.22.7.0.255:820.1
1.0.23.7.0.255:830.2
1.0.32.7.0.255:230.5
1.0.52.7.0.255:228.3
1.0.72.7.0.255:232.1
1.0.31.7.0.255:3.7
1.0.51.7.0.255:3.6
1.0.71.7.0.255:3.6
"""
        elif self.meter_type == "gas":
            return """
7.0.0.0.0.255:87654321
7.0.1.7.0.255:2.5
7.0.1.8.0.255:1234.56
"""
        elif self.meter_type == "water":
            return """
8.0.0.0.0.255:11223344
8.0.1.7.0.255:1.2
8.0.1.8.0.255:567.89
"""
        else:
            return ""


# Factory functions and backward compatibility
def create_obis_reader(
    device_id: str,
    meter_type: str = "electricity",
    **kwargs
) -> OBISReader:
    """
    Factory function to create an OBIS reader.
    
    Args:
        device_id: Device identifier
        meter_type: Type of meter
        **kwargs: Additional arguments
        
    Returns:
        Configured OBISReader instance
    """
    return OBISReader(device_id, meter_type, **kwargs)


def read_obis_data(
    device_id: str,
    meter_type: str,
    raw_data: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Read OBIS data from raw meter data (backward compatibility function).
    
    Args:
        device_id: Device identifier
        meter_type: Type of meter
        raw_data: Raw data from meter
        **kwargs: Additional arguments
        
    Returns:
        Dictionary of OBIS data
    """
    reader = OBISReader(device_id, meter_type, **kwargs)
    meter_data = reader.read_obis_data(raw_data)
    
    # Convert to simple format
    results = {}
    for obis_code, data in meter_data.items():
        results[obis_code] = {
            "value": data.value,
            "unit": data.unit,
            "timestamp": data.timestamp,
            "quality": data.quality
        }
    
    return results