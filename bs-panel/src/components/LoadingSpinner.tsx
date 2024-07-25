import React from "react";
import { Spinner, SpinnerSize } from "@blueprintjs/core";

const LoadingSpinner: React.FC = () => (
  <div className="flex justify-center items-center h-screen">
    <Spinner size={SpinnerSize.LARGE} />
  </div>
);

export default LoadingSpinner;
