import React from "react";
import { Spinner, SpinnerSize } from "@blueprintjs/core";

const LoadingSpinner: React.FC = () => (
  <div className="flex justify-center items-center h-full">
    <Spinner size={SpinnerSize.LARGE} />
  </div>
);

export default LoadingSpinner;
