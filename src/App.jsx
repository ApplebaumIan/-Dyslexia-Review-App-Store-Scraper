import * as React from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import ProTip from './ProTip';
import Copyright from './Copyright';
import {Card, CardContent, Paper} from "@mui/material";
import { DataGrid } from '@mui/x-data-grid';
import {useEffect, useState} from "react";
import Rating from '@mui/material/Rating';

function RenderRating(props){
    const {value} = props;
    return <Rating value={value} readOnly />
}

const columns = [
    { field: 'id', headerName: 'ID', width: 20 },
    { field: 'app_name', headerName: 'App', width: 100 },
    { field: 'rating', headerName: 'Rating', width: 130 ,
        renderCell: RenderRating },
    { field: 'title', headerName: 'Title', width: 130 },
    { field: 'content', headerName: 'Content', width: 300 },
    { field: 'author', headerName: 'Author', width: 130 },
];


const paginationModel = { page: 0, pageSize: 10 };

export default function App() {
    const [rows,setRow] = useState([])
    const [hobbie,setHobbie] = useState(null)
    const [test,setTest] = useState(null)
    useEffect(()=>{
        const requestOptions = {
            method: "GET",
            redirect: "follow",
            // mode: 'no-cors',

        };


        // fetch("http://localhost:3000/blah", requestOptions)
        //     .then((response) => response.json())
        //     .then((result) => result)
        //     .catch((error) => console.error(error));


        // setRow( [
        //     { id: 1, app_name: "big booty club", rating: 5, title: 'This App is great', content:"Axonas sunt calceuss de noster buxum.", author: "applebaumian" },
        //     { id: 2, app_name: "big booty club", rating: 1, title: 'This App is bad', content:"Axonas sunt calceuss de noster buxum.", author: "applebaumian" },
        // ])

           fetch("/reviews", requestOptions)
            .then((response) => response.json())
            .then((result) =>   setRow(result))
            .catch((error) => console.error(error));
    },[])

  return (
    <Container maxWidth="m" >
      <Box sx={{ my: 4 }}>
          <Paper sx={{ height: "90vh", width: '100%' }}>
              <DataGrid
                  rows={rows}
                  columns={columns}
                  initialState={{ pagination: { paginationModel } }}
                  pageSizeOptions={[10,20,50]}
                  getRowHeight={() => 'auto'}
                  sx={{ border: 0 }}
              />
          </Paper>
      </Box>
    </Container>
  );
}
