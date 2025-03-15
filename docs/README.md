# F1 Clash Manager

A comprehensive data management tool for F1 Clash game, built with Streamlit.

## Features

- **Loadouts Manager**: Create, edit, and compare car and driver loadouts
- **Series Loadouts**: Organize loadouts by series and get series-specific recommendations
- **Drivers Manager**: Manage driver data and statistics
- **Components Manager**: Manage car components and their stats
- **Tracks Manager**: View track information and recommended setups
- **Series Setups**: View recommended setups for each series
- **Import Tools**: Import data from spreadsheets and other sources
- **Automatic Highest Level Calculation**: Calculate the highest possible level for drivers and components based on cards owned

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

### Loadouts Manager

The Loadouts Manager allows you to create and manage car and driver loadouts for different race strategies. You can:

- Create new loadouts with specific car components and drivers
- View detailed stats for each loadout
- Compare loadouts to find the best setup for each track
- See track recommendations for each loadout
- Match loadouts to the best series based on track stats

### Series Loadouts

The Series Loadouts feature helps you organize your loadouts by series and recommend the best loadouts for each series:

- View loadouts organized by series (Grand Prix, Series 8, Series 9, Series 10+)
- See recommended loadouts for each series based on dominant track stats
- For rotating series (10, 11, 12), set the current dominant stat and get recommendations
- Easily navigate between series and find the optimal loadout for each

### Drivers Manager

The Drivers Manager helps you keep track of your driver collection. You can:

- View all available drivers and their stats
- Filter drivers by rarity, level, and other attributes
- Export driver data to CSV for editing
- Import updated driver data from CSV

### Components Manager

The Components Manager helps you manage your car components. You can:

- View components by type (Brakes, Gearbox, Rear Wing, Front Wing, Suspension, Engine)
- Filter components by rarity and inventory status
- Export component data to CSV for editing
- Import updated component data from CSV

### Tracks Manager

The Tracks Manager provides information about all tracks in the game. You can:

- View track details including primary attributes and focus areas
- See recommended boosts for each track
- Filter tracks by attribute and focus area

### Series Setups

The Series Setups section shows recommended component setups for each series. You can:

- View recommended setups for Speed, Cornering, and Power Unit focus
- See component values and total stats for each setup

### Import Tools

The Import Tools section allows you to import data from specialized CSV formats:

- Components Vertical CSV - with component types as section headers
- Drivers Vertical Combined CSV - with driver stats and details
- Data Input & Tracker CSV - with level requirements and card tracking
  - Now with automatic highest level calculation based on cards owned
- Series Information CSV - with series stats and track information

#### New Highest Level Calculation

The tool now automatically calculates the highest possible level for drivers and components based on the number of cards owned, implementing the same logic from the F1 Clash Resource Sheet:

1. Import your data from the Data Input & Tracker CSV
2. The tool will automatically calculate the highest possible level for each item
3. All JSON files will be updated with the calculated values

This replaces the manual calculation that previously had to be done in the spreadsheet before importing.

## Data Structure

The application uses the following JSON files to store data:

- `drivers.json`: Driver data
- `components_*.json`: Component data for each type
- `track_boosts.json`: Track and boost data
- `series_setups.json`: Series setup recommendations
- `loadouts.json`: Loadout configurations
- `series_data.json`: Series information with track stats and recommendations
- `rotating_series.json`: Current track stats for rotating series (10-12)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 