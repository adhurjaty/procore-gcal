import React from 'react';
import Flash from '../components/Flash';

export default function TestBed() {
    return (
        <Flash visibility={true} isSuccess={true} message="success" />
    )
}