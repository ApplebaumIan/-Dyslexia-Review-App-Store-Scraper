import * as React from 'react';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import { Paper, Select, MenuItem, InputLabel, FormControl } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { useEffect, useState } from 'react';
import Rating from '@mui/material/Rating';

function RenderRating(props) {
    const { value } = props;
    return <Rating value={value} readOnly />;
}

const columns = [
    { field: 'id', headerName: 'ID', width: 20 },
    { field: 'app_name', headerName: 'App', width: 100 },
    { field: 'rating', headerName: 'Rating', width: 130, renderCell: RenderRating },
    { field: 'title', headerName: 'Title', width: 130 },
    { field: 'content', headerName: 'Content', width: 300 },
    { field: 'author', headerName: 'Author', width: 130 },
];

const paginationModel = { page: 0, pageSize: 10 };

export default function App() {
    const [rows, setRows] = useState([]);
    const [filteredRows, setFilteredRows] = useState([]);
    const [appNames, setAppNames] = useState([]);
    const [selectedApp, setSelectedApp] = useState("");

    useEffect(() => {
        const requestOptions = {
            method: "GET",
            redirect: "follow",
        };

        fetch("/reviews", requestOptions)
            .then((response) => response.json())
            .then((result) => {
                setRows(result);
                setFilteredRows(result);

                // Extract unique app names
                const uniqueAppNames = Array.from(new Set(result.map((row) => row.app_name)));
                setAppNames(uniqueAppNames);
            })
            .catch((error) => console.error(error));
    }, []);

    // Handle dropdown change
    const handleAppChange = (event) => {
        const appName = event.target.value;
        setSelectedApp(appName);

        // Filter rows based on the selected app
        if (appName === "") {
            setFilteredRows(rows); // Show all rows if no app is selected
        } else {
            setFilteredRows(rows.filter((row) => row.app_name === appName));
        }
    };

    return (
        <Container maxWidth="m">
            <Box sx={{ my: 4 }}>
                {/* Dropdown Menu for Filtering */}
                <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel id="app-select-label">Filter by App</InputLabel>
                    <Select
                        labelId="app-select-label"
                        value={selectedApp}
                        onChange={handleAppChange}
                        displayEmpty
                    >
                        <MenuItem value="">
                            <em>All Apps</em>
                        </MenuItem>
                        {appNames.map((appName) => (
                            <MenuItem key={appName} value={appName}>
                                {appName}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>

                <Paper sx={{ height: "90vh", width: '100%' }}>
                    <DataGrid
                        rows={filteredRows}
                        columns={columns}
                        initialState={{ pagination: { paginationModel } }}
                        pageSizeOptions={[10, 20, 50]}
                        getRowHeight={() => 'auto'}
                        sx={{ border: 0 }}
                    />
                </Paper>
            </Box>
        </Container>
    );
}
